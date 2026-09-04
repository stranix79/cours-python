# src/statusboard/models.py — Labo 21 (solution) : les tables, en SQLModel.
#
# Rôle : une classe = une table (table=True) ; les classes sans table= sont les
# schémas d'entrée/sortie de l'API (pydantic pur, chapitre 17 et 18).
# Utilisé par : db.py, worker.py, api.py, cli.py.
"""Modèles : cibles surveillées, résultats de vérification, utilisateurs."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class Kind(StrEnum):
    """Les trois façons de vérifier une cible."""

    http = "http"  # GET sur une URL, OK si statut < 400
    tcp = "tcp"  # connexion TCP à hôte:port
    ping = "ping"  # la commande ping du système, 1 paquet


class TargetBase(SQLModel):
    """Champs communs entre ce qu'on reçoit (création) et ce qu'on stocke."""

    name: str = Field(index=True, unique=True)
    kind: Kind
    address: str  # URL pour http, "hôte:port" pour tcp, hôte pour ping
    interval_s: float = 30.0
    enabled: bool = True


class Target(TargetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class TargetCreate(TargetBase):
    """Ce que le client POST : pas d'id, c'est la base qui le donne."""


class Check(SQLModel, table=True):
    """Une vérification, horodatée. L'historique d'une cible = ses Check."""

    id: int | None = Field(default=None, primary_key=True)
    target_id: int = Field(foreign_key="target.id", index=True)
    at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ok: bool
    latency_ms: float | None = None
    detail: str = ""  # "200 OK", "timeout", "connection refused"…


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str


class TargetStatus(SQLModel):
    """Vue « état courant » d'une cible : la cible + son dernier check. Sortie API seulement."""

    target: Target
    ok: bool | None = None  # None : jamais vérifiée
    at: datetime | None = None
    latency_ms: float | None = None
    detail: str = ""
