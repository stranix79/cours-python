# app/main.py — Labo 19 : l'application. Lancer : uvicorn app.main:app --reload
#
# Rôle : cycle de vie (tables + admin au démarrage), middlewares (CORS, chrono),
# gestion globale des erreurs, routeurs, /health.

import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from .config import settings
from .db import create_db_and_tables, engine
from .models import User
from .routers import auth, tickets
from .security import hacher

# Sans basicConfig, nos log.info() n'apparaîtraient pas : le logger racine
# est au niveau WARNING par défaut (chapitre 8). Uvicorn configure les siens,
# pas les nôtres.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("tickets")


def bootstrap_admin(moteur=engine) -> None:
    """Crée le compte admin s'il n'existe pas. Le mot de passe vient de
    TICKETS_ADMIN_PASSWORD : c'est ainsi qu'on amorce une app sans écran de setup.
    Le paramètre permet aux tests de passer leur base en mémoire."""
    with Session(moteur) as session:
        if session.exec(select(User).where(User.username == "admin")).first() is None:
            session.add(User(username="admin", hashed_password=hacher(settings.admin_password), is_admin=True))
            session.commit()
            log.info("compte admin créé")


# lifespan : ce qui est avant le yield tourne au démarrage, ce qui est après
# à l'arrêt (fermer un pool, vider un cache...). Même idée que get_session.
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    bootstrap_admin()
    yield


app = FastAPI(
    title="Tickets d'incidents",
    description="Labo 19 : API complète avec base SQLite, JWT et rôles.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS : un navigateur refuse qu'une page servie par http://localhost:5173
# appelle http://localhost:8000 sauf si CE serveur l'autorise explicitement.
# curl et les autres serveurs ne sont pas concernés : c'est une protection du navigateur.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Un middleware voit TOUTES les requêtes, avant et après la route. Ici : on
# chronomètre, on logue, on ajoute un en-tête. Un endroit pour un id de
# corrélation, une métrique Prometheus, un rate-limit...
@app.middleware("http")
async def chrono(request: Request, call_next):
    debut = time.perf_counter()
    response = await call_next(request)
    duree_ms = (time.perf_counter() - debut) * 1000
    response.headers["X-Process-Time"] = f"{duree_ms:.1f}ms"
    log.info("%s %s -> %s en %.1f ms", request.method, request.url.path, response.status_code, duree_ms)
    return response


# Gestionnaire global : une contrainte UNIQUE violée n'importe où devient un
# 409 propre au lieu d'un 500 avec une trace SQLAlchemy.
@app.exception_handler(IntegrityError)
async def integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": "Conflit : cette valeur existe déjà"})


app.include_router(auth.router)
app.include_router(tickets.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}
