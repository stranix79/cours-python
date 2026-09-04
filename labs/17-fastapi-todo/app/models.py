# app/models.py — Labo 17 : les modèles pydantic = la forme des données de l'API.

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Severite(str, Enum):
    BASSE = "basse"
    MOYENNE = "moyenne"
    HAUTE = "haute"
    CRITIQUE = "critique"


class Statut(str, Enum):
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    RESOLU = "resolu"


class TicketCreate(BaseModel):
    """Body du POST : ce que le client envoie pour créer un ticket."""

    titre: str = Field(min_length=3, max_length=120, examples=["Disque plein sur srv-db-01"])
    description: str = ""
    severite: Severite = Severite.MOYENNE


class TicketReplace(TicketCreate):
    """Body du PUT : un ticket complet, statut compris."""

    statut: Statut = Statut.OUVERT


class TicketUpdate(BaseModel):
    """Body du PATCH : tout est optionnel."""

    # TODO : les mêmes champs que TicketReplace, mais chacun `X | None = None`.
    #   Garde la contrainte de longueur sur titre : Field(default=None, min_length=3, max_length=120)
    pass


class Ticket(TicketCreate):
    """Un ticket côté serveur, et ce qu'on renvoie au client."""

    id: int
    statut: Statut = Statut.OUVERT
    cree_le: datetime
