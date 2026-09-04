# app/deps.py — Labo 19 : les dépendances partagées (utilisateur courant, admin, pagination).
#
# Utilisé par : les routeurs, via Depends(...).
#
# Une dépendance est une fonction (ou une classe) que FastAPI appelle AVANT la
# route et dont il injecte le résultat en paramètre. Elle peut elle-même
# dépendre d'autres dépendances : get_current_user dépend du jeton ET de la session.

from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from .db import get_session
from .models import User
from .security import decoder_token

# OAuth2PasswordBearer fait deux choses : il lit l'en-tête
# `Authorization: Bearer <token>` (401 s'il manque), et il dit à /docs où
# obtenir un jeton, ce qui active le bouton « Authorize » dans Swagger UI.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Annotated[Type, Depends(f)] : le type pour l'éditeur, la dépendance pour
# FastAPI. On définit l'alias une fois et on le réutilise dans chaque route.
SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(token: TokenDep, session: SessionDep) -> User:
    """Du jeton à l'utilisateur en base. 401 dans tous les cas d'échec."""
    # TODO : username = decoder_token(token) ; None → HTTPException 401 avec
    #        headers={"WWW-Authenticate": "Bearer"} (l'en-tête fait partie du protocole).
    #        Puis chercher le User en base (select(User).where(User.username == ...)).first() ;
    #        absent → 401 aussi. Renvoyer le User.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="TODO get_current_user")


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin(user: CurrentUser) -> User:
    """Une dépendance qui dépend d'une autre : d'abord authentifié, puis admin.
    401 = « je ne sais pas qui tu es », 403 = « je sais, et tu n'as pas le droit »."""
    # TODO : si not user.is_admin → 403. Sinon renvoyer user.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="TODO require_admin")


AdminUser = Annotated[User, Depends(require_admin)]


class Pagination:
    """Une dépendance sous forme de classe : FastAPI lit offset et limit dans la
    query string et construit l'objet. Réutilisable par toutes les routes de liste."""

    def __init__(
        self,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=50, ge=1, le=200),
    ):
        self.offset = offset
        self.limit = limit


PaginationDep = Annotated[Pagination, Depends()]   # Depends() vide : « utilise le type lui-même »
