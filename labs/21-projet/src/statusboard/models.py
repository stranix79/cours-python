# src/statusboard/models.py — Labo 21 : les tables SQLModel et les schémas de l'API (jalon 1).
"""Modèles : cibles surveillées, résultats de vérification, utilisateurs."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class Kind(StrEnum):
    http = "http"
    tcp = "tcp"
    ping = "ping"


class TargetBase(SQLModel):
    name: str = Field(index=True, unique=True)
    kind: Kind
    address: str
    interval_s: float = 30.0
    enabled: bool = True


class Target(TargetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class TargetCreate(TargetBase):
    """Ce que le client POST."""


class Check(SQLModel, table=True):
    # TODO : id, target_id (clé étrangère vers target.id, indexée), at (défaut : maintenant en UTC,
    #        via default_factory), ok, latency_ms (optionnel), detail (chaîne, défaut "").
    id: int | None = Field(default=None, primary_key=True)
    target_id: int = Field(foreign_key="target.id", index=True)
    at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ok: bool


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str


class TargetStatus(SQLModel):
    """Une cible + son dernier check (ok=None si jamais vérifiée). Sortie API seulement."""

    target: Target
    ok: bool | None = None
    at: datetime | None = None
    latency_ms: float | None = None
    detail: str = ""
