# app/store.py — Labo 17 : le « stockage », c'est-à-dire un simple dict en mémoire.
#
# Utilisé par : routers/tickets.py.
#
# Un dict {id: Ticket} suffit pour apprendre les routes. Il a deux défauts
# évidents qu'on corrige au chapitre 18 : tout disparaît quand le serveur
# s'arrête, et deux workers uvicorn auraient chacun leur dict.

import itertools
from datetime import datetime, timezone

from .models import Severite, Ticket, TicketCreate

TICKETS: dict[int, Ticket] = {}

# itertools.count(1) est un itérateur infini 1, 2, 3, ... : next(_ids) donne
# le prochain id. Plus simple qu'un compteur global à incrémenter à la main.
_ids = itertools.count(1)


def creer(donnees: TicketCreate) -> Ticket:
    """Crée un Ticket à partir des données validées, l'enregistre, le renvoie."""
    ticket = Ticket(
        id=next(_ids),
        cree_le=datetime.now(timezone.utc),
        # model_dump() transforme le modèle en dict : {"titre": ..., "description": ...}.
        # Le ** l'éclate en arguments nommés (chapitre 5).
        **donnees.model_dump(),
    )
    TICKETS[ticket.id] = ticket
    return ticket


def vider() -> None:
    """Remet le stockage à zéro. Utilisé par les tests."""
    global _ids
    TICKETS.clear()
    _ids = itertools.count(1)


def peupler() -> None:
    """Quelques tickets de démonstration pour ne pas démarrer avec une liste vide."""
    creer(TicketCreate(titre="Disque plein sur srv-db-01", severite=Severite.HAUTE))
    creer(TicketCreate(titre="Certificat TLS expire dans 7 jours", severite=Severite.MOYENNE))
    creer(TicketCreate(titre="Typo dans le MOTD", severite=Severite.BASSE))
