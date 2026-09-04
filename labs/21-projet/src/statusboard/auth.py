# src/statusboard/auth.py — Labo 21 : mots de passe (bcrypt) et jetons JWT (jalon 4).
"""Authentification : bcrypt + JWT."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from statusboard.db import get_session
from statusboard.models import User

ALGO = "HS256"
oauth2 = OAuth2PasswordBearer(tokenUrl="token")


def hacher(mot_de_passe: str) -> str:
    # TODO : bcrypt.hashpw(mot_de_passe.encode(), bcrypt.gensalt()).decode()
    raise NotImplementedError("TODO jalon 4")


def verifier(mot_de_passe: str, hash_: str) -> bool:
    raise NotImplementedError("TODO jalon 4")


def creer_token(username: str) -> str:
    # TODO : jwt.encode({"sub": username, "exp": maintenant + token_minutes}, secret, algorithm=ALGO)  (PyJWT)
    raise NotImplementedError("TODO jalon 4")


def authentifier(session: Session, username: str, mot_de_passe: str) -> User | None:
    raise NotImplementedError("TODO jalon 4")


def get_current_user(
    token: Annotated[str, Depends(oauth2)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """Décode le Bearer token, charge l'utilisateur, ou HTTPException 401."""
    raise NotImplementedError("TODO jalon 4")


def assurer_admin(session: Session) -> None:
    """Crée le compte admin (get_settings().admin_user / admin_password) s'il n'existe pas."""
    raise NotImplementedError("TODO jalon 4")
