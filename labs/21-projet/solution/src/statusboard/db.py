# src/statusboard/db.py — Labo 21 (solution) : moteur SQLAlchemy et sessions.
#
# Rôle : un engine unique (créé paresseusement), la création des tables, et la
# dépendance FastAPI get_session (chapitre 18 et 19).
# Utilisé par : api.py, worker.py, cli.py, tests.
"""Accès à la base : engine, init, sessions."""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from statusboard.config import get_settings
from statusboard.models import Check, Target, TargetStatus


@lru_cache
def get_engine() -> Engine:
    url = get_settings().database_url
    # SQLite refuse par défaut qu'une connexion change de thread ; or le worker
    # async et les handlers FastAPI (threadpool) s'en servent. On le désactive :
    # SQLAlchemy sérialise les accès de son côté.
    args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    if url in ("sqlite://", "sqlite:///:memory:"):
        # Base en mémoire (tests) : chaque connexion SQLite aurait SA base vide.
        # StaticPool force une connexion unique partagée par tous les threads.
        return create_engine(url, connect_args=args, poolclass=StaticPool)
    return create_engine(url, connect_args=args)


def init_db() -> None:
    SQLModel.metadata.create_all(get_engine())


def get_session() -> Iterator[Session]:
    """Dépendance FastAPI : une session par requête, fermée à la fin (yield, chapitre 19)."""
    with Session(get_engine()) as session:
        yield session


def status_of(session: Session, target: Target) -> TargetStatus:
    """La cible et son dernier check, ou None partout si jamais vérifiée."""
    last = session.exec(
        select(Check).where(Check.target_id == target.id).order_by(Check.at.desc()).limit(1)  # type: ignore[union-attr]
    ).first()
    if last is None:
        return TargetStatus(target=target)
    return TargetStatus(
        target=target, ok=last.ok, at=last.at, latency_ms=last.latency_ms, detail=last.detail
    )
