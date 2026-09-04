# app/models.py — Labo 17 : les modèles pydantic, c'est-à-dire la FORME des données
# qui entrent et sortent de l'API.
#
# Utilisé par : routers/tickets.py (types des paramètres et des réponses).
#
# Un BaseModel pydantic est une classe dont les attributs annotés deviennent des
# champs validés : si un client envoie {"titre": 42}, pydantic renvoie une
# erreur 422 détaillée AVANT que notre code ne soit appelé. C'est le contrat
# de l'API, et c'est lui que FastAPI publie dans /docs.

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Severite(str, Enum):
    # Hériter de str ET de Enum : la valeur est une chaîne ("haute"), donc
    # elle se sérialise en JSON telle quelle, et FastAPI propose la liste des
    # valeurs possibles dans la doc (un menu déroulant dans Swagger UI).
    BASSE = "basse"
    MOYENNE = "moyenne"
    HAUTE = "haute"
    CRITIQUE = "critique"


class Statut(str, Enum):
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    RESOLU = "resolu"


class TicketCreate(BaseModel):
    """Ce que le client envoie pour créer un ticket (le body du POST)."""

    # Field() ajoute des contraintes : ici la longueur. Elles sont vérifiées
    # par pydantic et affichées dans la doc.
    titre: str = Field(min_length=3, max_length=120, examples=["Disque plein sur srv-db-01"])
    description: str = ""
    severite: Severite = Severite.MOYENNE


class TicketReplace(TicketCreate):
    """Body du PUT : un ticket complet, statut compris (remplacement total)."""

    statut: Statut = Statut.OUVERT


class TicketUpdate(BaseModel):
    """Body du PATCH : tout est optionnel, on ne modifie que ce qui est envoyé."""

    # `str | None = None` : le champ peut être absent. Dans la route, on
    # utilisera model_dump(exclude_unset=True) pour ne garder que les champs
    # réellement présents dans le JSON reçu.
    titre: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = None
    severite: Severite | None = None
    statut: Statut | None = None


class Ticket(TicketCreate):
    """Un ticket tel qu'il existe côté serveur : les champs du client + ceux qu'on
    ajoute nous-mêmes (id, statut, date). C'est aussi ce qu'on renvoie au client."""

    id: int
    statut: Statut = Statut.OUVERT
    cree_le: datetime
