# app/routers/tickets.py — Labo 17 : toutes les routes /tickets.
#
# Importé par : app/main.py, qui fait app.include_router(router).
#
# Un APIRouter est un « mini FastAPI » : on y déclare des routes exactement
# comme sur l'app, puis on le branche sur l'app avec un préfixe. Ça permet de
# découper une API en fichiers (tickets.py, users.py...) au lieu d'un main.py
# de 2000 lignes.

from fastapi import APIRouter, HTTPException, Query, status

from .. import store
from ..models import Severite, Statut, Ticket, TicketCreate, TicketReplace, TicketUpdate

# prefix : toutes les routes ci-dessous commencent par /tickets.
# tags : regroupe les routes dans /docs sous un même titre.
router = APIRouter(prefix="/tickets", tags=["tickets"])


def _trouver(ticket_id: int) -> Ticket:
    """Renvoie le ticket ou lève un 404. Factorisé : quatre routes en ont besoin."""
    ticket = store.TICKETS.get(ticket_id)
    if ticket is None:
        # HTTPException interrompt la route : FastAPI renvoie {"detail": "..."}
        # avec le code demandé. Pas besoin de return.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket {ticket_id} introuvable")
    return ticket


# response_model=list[Ticket] : FastAPI valide ET documente la réponse, et
# filtre tout champ qui ne serait pas dans Ticket (utile quand on renvoie un
# objet BDD avec un mot de passe haché dedans, chapitre 19).
@router.get("", response_model=list[Ticket])
def lister(
    # Un paramètre qui n'est pas dans le chemin est un paramètre de requête :
    # GET /tickets?statut=ouvert&severite=haute. Optionnel grâce au = None.
    statut: Statut | None = None,
    severite: Severite | None = None,
    # Query() sert à ajouter des contraintes ou une description à un paramètre
    # de requête. ge/le = greater/less or equal.
    limite: int = Query(default=100, ge=1, le=1000, description="Nombre max de tickets renvoyés"),
) -> list[Ticket]:
    tickets = list(store.TICKETS.values())
    if statut is not None:
        tickets = [t for t in tickets if t.statut == statut]
    if severite is not None:
        tickets = [t for t in tickets if t.severite == severite]
    return tickets[:limite]


# status_code=201 : « Created », le code standard pour un POST qui crée.
# Sans ça, FastAPI renverrait 200.
@router.post("", response_model=Ticket, status_code=status.HTTP_201_CREATED)
def creer(donnees: TicketCreate) -> Ticket:
    # `donnees: TicketCreate` : un paramètre dont le type est un BaseModel est
    # lu dans le BODY JSON de la requête. Pydantic l'a déjà validé : si on
    # arrive ici, les données sont bonnes.
    return store.creer(donnees)


# {ticket_id} dans le chemin + `ticket_id: int` dans la signature : FastAPI
# convertit "12" en 12, et répond 422 tout seul si on lui donne "abc".
@router.get("/{ticket_id}", response_model=Ticket)
def lire(ticket_id: int) -> Ticket:
    return _trouver(ticket_id)


@router.put("/{ticket_id}", response_model=Ticket)
def remplacer(ticket_id: int, donnees: TicketReplace) -> Ticket:
    ancien = _trouver(ticket_id)
    # PUT = remplacement complet : on repart des données reçues, on ne garde
    # de l'ancien que ce que le client ne peut pas décider (id, date de création).
    nouveau = Ticket(id=ancien.id, cree_le=ancien.cree_le, **donnees.model_dump())
    store.TICKETS[ticket_id] = nouveau
    return nouveau


@router.patch("/{ticket_id}", response_model=Ticket)
def modifier(ticket_id: int, donnees: TicketUpdate) -> Ticket:
    ancien = _trouver(ticket_id)
    # exclude_unset=True : seulement les champs présents dans le JSON reçu.
    # Sans ça, un PATCH {"statut": "resolu"} écraserait titre et severite avec None.
    changements = donnees.model_dump(exclude_unset=True)
    # model_copy(update=...) renvoie un nouveau modèle avec les champs modifiés :
    # les modèles pydantic se manipulent comme des valeurs, pas comme des
    # structs qu'on patche sur place.
    nouveau = ancien.model_copy(update=changements)
    store.TICKETS[ticket_id] = nouveau
    return nouveau


# 204 No Content : succès, et rien dans le corps de la réponse. On ne renvoie
# donc rien (None), et on ne met pas de response_model.
@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer(ticket_id: int) -> None:
    _trouver(ticket_id)
    del store.TICKETS[ticket_id]
