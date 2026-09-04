# app/models.py — Labo 19 : les modèles SQLModel = tables ET schémas de l'API.
#
# Utilisé par : db.py, routers/*, deps.py.
#
# Le découpage standard : une classe « Base » avec les champs communs (sans
# table=True), une classe table qui hérite et ajoute id + colonnes internes,
# et des classes pydantic pures pour ce que l'API reçoit (Create, Update) et
# renvoie (Public). Ainsi le mot de passe haché, en base, ne sort jamais.

from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


def maintenant() -> datetime:
    return datetime.now(timezone.utc)


# ---------- utilisateurs ----------

class UserBase(SQLModel):
    username: str = Field(min_length=3, max_length=32, index=True, unique=True)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str          # jamais le mot de passe, toujours son hachage
    is_admin: bool = False
    tickets: list["Ticket"] = Relationship(back_populates="owner")


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)   # 72 : la limite de bcrypt


class UserPublic(UserBase):
    id: int
    is_admin: bool


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# ---------- tickets ----------

class Severite(str, Enum):
    BASSE = "basse"
    MOYENNE = "moyenne"
    HAUTE = "haute"
    CRITIQUE = "critique"


class Statut(str, Enum):
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    RESOLU = "resolu"


class TicketBase(SQLModel):
    titre: str = Field(min_length=3, max_length=120)
    description: str = ""
    severite: Severite = Severite.MOYENNE


class Ticket(TicketBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    statut: Statut = Statut.OUVERT
    # default_factory : la fonction est appelée à chaque création (un
    # `default=maintenant()` serait évalué UNE fois, à l'import : piège classique).
    cree_le: datetime = Field(default_factory=maintenant)
    owner_id: int = Field(foreign_key="user.id", index=True)
    owner: User | None = Relationship(back_populates="tickets")


class TicketCreate(TicketBase):
    pass


class TicketUpdate(SQLModel):
    titre: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = None
    severite: Severite | None = None
    statut: Statut | None = None


class TicketPublic(TicketBase):
    id: int
    statut: Statut
    cree_le: datetime
    owner_id: int
