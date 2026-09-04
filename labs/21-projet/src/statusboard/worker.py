# src/statusboard/worker.py — Labo 21 : la boucle de surveillance (jalon 3).
"""Le worker asynchrone : tick() vérifie les cibles dues, boucle() tourne jusqu'à annulation."""

import asyncio
import logging

from statusboard.models import Check, Target

log = logging.getLogger(__name__)


async def verifier_et_sauver(target: Target) -> Check:
    """Vérifie, sauve le Check, publie un événement {"type": "check", "target": …, "ok": …,
    "changed": …, "latency_ms": …, "detail": …, "at": …}. Renvoie le Check."""
    raise NotImplementedError("TODO jalon 3")


async def tick() -> list[Check]:
    """Un tour : charger les cibles activées, garder celles dont l'intervalle est écoulé
    (ou jamais vérifiées), les vérifier en parallèle avec asyncio.gather."""
    raise NotImplementedError("TODO jalon 3")


async def boucle(periode_s: float = 1.0) -> None:
    log.info("worker démarré, période %.1fs", periode_s)
    while True:
        try:
            await tick()
        except Exception:  # noqa: BLE001
            log.exception("tick en erreur")
        await asyncio.sleep(periode_s)
