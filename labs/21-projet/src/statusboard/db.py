# src/statusboard/db.py — Labo 21 : engine, création des tables, sessions (jalon 1).
"""Accès à la base : engine, init, sessions."""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from statusboard.config import get_settings
from statusboard.models import Target, TargetStatus


@lru_cache
def get_engine() -> Engine:
    # TODO : pour SQLite, connect_args={"check_same_thread": False} ; pour "sqlite://"
    #        (mémoire, tests), poolclass=StaticPool sinon chaque thread a sa base vide.
    return create_engine(get_settings().database_url)


def init_db() -> None:
    SQLModel.metadata.create_all(get_engine())


def get_session() -> Iterator[Session]:
    """Dépendance FastAPI : une session par requête."""
    with Session(get_engine()) as session:
        yield session


def status_of(session: Session, target: Target) -> TargetStatus:
    """La cible et son dernier check (select … order_by(Check.at.desc()).limit(1))."""
    raise NotImplementedError("TODO jalon 1")
