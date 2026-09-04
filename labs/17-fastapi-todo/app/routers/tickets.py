# app/routers/tickets.py — Labo 17 : toutes les routes /tickets.
# Branché sur l'app par app/main.py (app.include_router).

from fastapi import APIRouter, HTTPException, Query, status

from .. import store
from ..models import Severite, Statut, Ticket, TicketCreate, TicketReplace, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _trouver(ticket_id: int) -> Ticket:
    """Renvoie le ticket ou lève un 404."""
    ticket = store.TICKETS.get(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket {ticket_id} introuvable")
    return ticket


@router.get("", response_model=list[Ticket])
def lister(
    statut: Statut | None = None,
    severite: Severite | None = None,
    limite: int = Query(default=100, ge=1, le=1000, description="Nombre max de tickets renvoyés"),
) -> list[Ticket]:
    tickets = list(store.TICKETS.values())
    if statut is not None:
        tickets = [t for t in tickets if t.statut == statut]
    # TODO : filtre aussi sur severite
    return tickets[:limite]


@router.get("/{ticket_id}", response_model=Ticket)
def lire(ticket_id: int) -> Ticket:
    return _trouver(ticket_id)


# TODO : POST /tickets → crée un ticket (store.creer), répond 201 avec le ticket.
#   Indices : @router.post("", response_model=Ticket, status_code=status.HTTP_201_CREATED)
#             le body se déclare comme un paramètre typé : donnees: TicketCreate
@router.post("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def creer():
    raise HTTPException(status_code=501, detail="TODO")


# TODO : PUT /tickets/{id} → remplacement complet (body TicketReplace).
#   On garde seulement id et cree_le de l'ancien ticket :
#   Ticket(id=ancien.id, cree_le=ancien.cree_le, **donnees.model_dump())
@router.put("/{ticket_id}")
def remplacer(ticket_id: int):
    raise HTTPException(status_code=501, detail="TODO")


# TODO : PATCH /tickets/{id} → modification partielle (body TicketUpdate).
#   Indices : donnees.model_dump(exclude_unset=True) ne garde que les champs envoyés ;
#             ancien.model_copy(update=changements) renvoie le ticket modifié.
@router.patch("/{ticket_id}")
def modifier(ticket_id: int):
    raise HTTPException(status_code=501, detail="TODO")


# TODO : DELETE /tickets/{id} → 204 sans corps (status_code=status.HTTP_204_NO_CONTENT),
#   404 si inexistant.
@router.delete("/{ticket_id}")
def supprimer(ticket_id: int):
    raise HTTPException(status_code=501, detail="TODO")
