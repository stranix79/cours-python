# src/statusboard/worker.py — Labo 21 (solution) : la boucle de surveillance.
#
# Rôle : toutes les `tick` secondes, charger les cibles actives, vérifier celles
# dont l'intervalle est écoulé, en parallèle (asyncio.gather), sauver le résultat
# et publier un événement. Tourne comme tâche de fond dans le lifespan de l'API.
# Utilisé par : api.py (lancement), tests/test_worker.py (un tick à la main).
"""Le worker asynchrone."""

import asyncio
import logging
from datetime import UTC, datetime

from sqlmodel import Session, select

from statusboard.bus import bus
from statusboard.checks import run_check
from statusboard.db import get_engine, status_of
from statusboard.models import Check, Target

log = logging.getLogger(__name__)


def _est_due(session: Session, target: Target, maintenant: datetime) -> bool:
    etat = status_of(session, target)
    if etat.at is None:
        return True
    # SQLite rend des datetimes naïfs : on les remet en UTC pour comparer.
    dernier = etat.at if etat.at.tzinfo else etat.at.replace(tzinfo=UTC)
    return (maintenant - dernier).total_seconds() >= target.interval_s


async def verifier_et_sauver(target: Target) -> Check:
    """Vérifie une cible, sauve le Check, publie l'événement. Renvoie le Check."""
    with Session(get_engine()) as session:
        avant = status_of(session, target).ok
    check = await run_check(target)  # la partie longue, sans tenir de session ouverte
    with Session(get_engine()) as session:
        session.add(check)
        session.commit()
        session.refresh(check)
    bus.publish(
        {
            "type": "check",
            "target": target.name,
            "ok": check.ok,
            "changed": avant is not None and avant != check.ok,
            "latency_ms": check.latency_ms,
            "detail": check.detail,
            "at": check.at.isoformat(),
        }
    )
    if avant is not None and avant != check.ok:
        log.warning("%s : %s → %s (%s)", target.name, avant, check.ok, check.detail)
    return check


async def tick() -> list[Check]:
    """Un tour de boucle : vérifie toutes les cibles dues, en parallèle."""
    maintenant = datetime.now(UTC)
    with Session(get_engine()) as session:
        cibles = session.exec(select(Target).where(Target.enabled)).all()  # type: ignore[arg-type]
        dues = [t for t in cibles if _est_due(session, t, maintenant)]
    if not dues:
        return []
    # gather : toutes les vérifications partent en même temps, on attend la plus lente.
    return list(await asyncio.gather(*(verifier_et_sauver(t) for t in dues)))


async def boucle(periode_s: float = 1.0) -> None:
    """Tourne jusqu'à annulation (CancelledError à l'arrêt de l'application)."""
    log.info("worker démarré, période %.1fs", periode_s)
    while True:
        try:
            await tick()
        except Exception:  # noqa: BLE001 : un tick raté ne doit pas tuer la boucle
            log.exception("tick en erreur")
        await asyncio.sleep(periode_s)
