# src/statusboard/api.py — Labo 21 (solution) : l'application FastAPI.
#
# Rôle : les routes REST, le flux SSE, et le lifespan qui crée les tables,
# l'admin, et lance le worker en tâche de fond.
# Lancé par : uvicorn statusboard.api:app, ou `statusboard serve`, ou les tests.
"""API REST + SSE de statusboard."""

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from statusboard import worker
from statusboard.auth import assurer_admin, authentifier, creer_token, get_current_user
from statusboard.bus import bus
from statusboard.config import get_settings
from statusboard.db import get_engine, get_session, init_db, status_of
from statusboard.models import Check, Target, TargetCreate, TargetStatus, User

log = logging.getLogger(__name__)

# Deux alias pour ne pas répéter les Depends dans chaque signature.
SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[User, Depends(get_current_user)]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Avant le yield : démarrage. Après : arrêt (chapitre 19)."""
    init_db()
    with Session(get_engine()) as session:
        assurer_admin(session)
    tache = None
    if get_settings().worker_enabled:
        tache = asyncio.create_task(worker.boucle())
        log.info("worker lancé en tâche de fond")
    yield
    if tache:
        tache.cancel()  # CancelledError dans la boucle → elle s'arrête
        with suppress(asyncio.CancelledError):
            await tache


app = FastAPI(title="statusboard", version="0.1.0", lifespan=lifespan)


# ---- Authentification --------------------------------------------------------


@app.post("/token")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> dict[str, str]:
    """Formulaire OAuth2 « password » : username + password → {access_token, token_type}."""
    user = authentifier(session, form.username, form.password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "identifiants invalides")
    return {"access_token": creer_token(user.username), "token_type": "bearer"}


# ---- Cibles ------------------------------------------------------------------


@app.get("/targets")
def lister(session: SessionDep) -> list[Target]:
    return list(session.exec(select(Target)).all())


@app.post("/targets", status_code=status.HTTP_201_CREATED)
def creer(donnees: TargetCreate, session: SessionDep, _: UserDep) -> Target:
    """Protégée : `_: UserDep` exige un jeton valide sans qu'on se serve de l'utilisateur."""
    if session.exec(select(Target).where(Target.name == donnees.name)).first():
        raise HTTPException(status.HTTP_409_CONFLICT, f"la cible {donnees.name!r} existe déjà")
    target = Target.model_validate(donnees)
    session.add(target)
    session.commit()
    session.refresh(target)
    return target


def _cible(session: Session, target_id: int) -> Target:
    target = session.get(Target, target_id)
    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "cible inconnue")
    return target


@app.delete("/targets/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer(target_id: int, session: SessionDep, _: UserDep) -> None:
    target = _cible(session, target_id)
    for check in session.exec(select(Check).where(Check.target_id == target_id)):
        session.delete(check)
    session.delete(target)
    session.commit()


@app.get("/targets/{target_id}/checks")
def historique(target_id: int, session: SessionDep, limit: int = 50) -> list[Check]:
    _cible(session, target_id)
    return list(
        session.exec(
            select(Check).where(Check.target_id == target_id).order_by(Check.at.desc()).limit(limit)  # type: ignore[union-attr]
        ).all()
    )


@app.post("/targets/{target_id}/check")
async def verifier_maintenant(target_id: int, session: SessionDep, _: UserDep) -> Check:
    """Vérification à la demande, sans attendre le worker."""
    return await worker.verifier_et_sauver(_cible(session, target_id))


# ---- État ---------------------------------------------------------------------


@app.get("/status")
def etat(session: SessionDep) -> list[TargetStatus]:
    """Chaque cible avec son dernier résultat : c'est ce qu'un tableau de bord affiche."""
    return [status_of(session, t) for t in session.exec(select(Target)).all()]


@app.get("/events")
async def evenements(session: SessionDep, limit: int | None = None) -> StreamingResponse:
    """Server-Sent Events (chapitre 16) : un instantané, puis chaque vérification en direct.

    `limit` : nombre d'événements après lesquels on ferme (pratique pour curl et
    les tests : sans lui le flux ne se termine jamais, ce qui est le but).
    """
    instantane = [s.model_dump(mode="json") for s in etat(session)]

    async def flux() -> AsyncIterator[str]:
        # Format SSE : "event: nom\ndata: json\n\n". Une ligne ": ..." est un
        # commentaire, qu'on envoie régulièrement pour garder la connexion vivante.
        yield f"event: snapshot\ndata: {json.dumps(instantane)}\n\n"
        envoyes = 0
        async with bus.subscribe() as file:
            while limit is None or envoyes < limit:
                try:
                    event = await asyncio.wait_for(file.get(), timeout=15)
                    yield f"event: check\ndata: {json.dumps(event)}\n\n"
                    envoyes += 1
                except TimeoutError:
                    yield ": keep-alive\n\n"

    return StreamingResponse(
        flux(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/health")
def health() -> dict[str, str | int]:
    return {"status": "ok", "sse_clients": bus.nb_abonnes}
