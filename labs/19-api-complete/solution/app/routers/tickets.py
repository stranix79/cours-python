# app/routers/tickets.py — Labo 19 : les tickets, persistants et liés à leur auteur.
#
# Branché par main.py sous /tickets. Toutes les routes exigent un utilisateur
# authentifié (CurrentUser) ; la suppression exige un admin.

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from ..deps import AdminUser, CurrentUser, PaginationDep, SessionDep
from ..models import Statut, Ticket, TicketCreate, TicketPublic, TicketUpdate, User

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _trouver(session, ticket_id: int, user: User) -> Ticket:
    """Le ticket, s'il existe ET que l'utilisateur a le droit de le voir.
    Un non-admin qui demande le ticket d'un autre reçoit 404, pas 403 : on ne
    confirme même pas que le ticket existe."""
    ticket = session.get(Ticket, ticket_id)
    if ticket is None or (not user.is_admin and ticket.owner_id != user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket {ticket_id} introuvable")
    return ticket


@router.get("", response_model=list[TicketPublic])
def lister(session: SessionDep, user: CurrentUser, page: PaginationDep, statut: Statut | None = None) -> list[Ticket]:
    requete = select(Ticket)
    if not user.is_admin:
        requete = requete.where(Ticket.owner_id == user.id)   # chacun voit les siens
    if statut is not None:
        requete = requete.where(Ticket.statut == statut)
    requete = requete.order_by(Ticket.id).offset(page.offset).limit(page.limit)
    return list(session.exec(requete))


@router.post("", response_model=TicketPublic, status_code=status.HTTP_201_CREATED)
def creer(donnees: TicketCreate, session: SessionDep, user: CurrentUser) -> Ticket:
    # model_validate avec update= : construit le Ticket (table) depuis le
    # TicketCreate (API) en ajoutant les champs que le client ne choisit pas.
    ticket = Ticket.model_validate(donnees, update={"owner_id": user.id})
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@router.get("/{ticket_id}", response_model=TicketPublic)
def lire(ticket_id: int, session: SessionDep, user: CurrentUser) -> Ticket:
    return _trouver(session, ticket_id, user)


@router.patch("/{ticket_id}", response_model=TicketPublic)
def modifier(ticket_id: int, donnees: TicketUpdate, session: SessionDep, user: CurrentUser) -> Ticket:
    ticket = _trouver(session, ticket_id, user)
    # sqlmodel_update : applique un dict de changements à un objet table.
    ticket.sqlmodel_update(donnees.model_dump(exclude_unset=True))
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer(ticket_id: int, session: SessionDep, admin: AdminUser) -> None:
    # `admin: AdminUser` suffit : si l'appelant n'est pas admin, la dépendance
    # a déjà répondu 403 (ou 401) et cette fonction n'est jamais entrée.
    ticket = session.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticket {ticket_id} introuvable")
    session.delete(ticket)
    session.commit()
