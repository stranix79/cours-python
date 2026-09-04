# src/statusboard/auth.py — Labo 21 (solution) : mots de passe et jetons JWT.
#
# Rôle : hacher/vérifier un mot de passe (bcrypt), émettre/valider un JWT
# (PyJWT), et la dépendance get_current_user qui protège les routes
# (chapitre 19).
# Utilisé par : api.py, cli.py (création de l'admin).
"""Authentification : bcrypt + JWT."""

from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
import jwt  # le paquet PyJWT, celui de la doc FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from statusboard.config import get_settings
from statusboard.db import get_session
from statusboard.models import User

ALGO = "HS256"
# tokenUrl : où le client obtient un jeton ; sert surtout au bouton Authorize de /docs.
oauth2 = OAuth2PasswordBearer(tokenUrl="token")


def hacher(mot_de_passe: str) -> str:
    # bcrypt sale et itère lui-même ; le résultat contient le sel. On l'appelle
    # directement : passlib, la surcouche historique, ne suit plus bcrypt 5.
    return bcrypt.hashpw(mot_de_passe.encode(), bcrypt.gensalt()).decode()


def verifier(mot_de_passe: str, hash_: str) -> bool:
    return bcrypt.checkpw(mot_de_passe.encode(), hash_.encode())


def creer_token(username: str) -> str:
    settings = get_settings()
    exp = datetime.now(UTC) + timedelta(minutes=settings.token_minutes)
    # Le JWT est signé, pas chiffré : n'importe qui peut lire "sub", personne ne peut le modifier.
    return jwt.encode({"sub": username, "exp": exp}, settings.secret_key, algorithm=ALGO)


def authentifier(session: Session, username: str, mot_de_passe: str) -> User | None:
    user = session.exec(select(User).where(User.username == username)).first()
    if user and verifier(mot_de_passe, user.password_hash):
        return user
    return None


def get_current_user(
    token: Annotated[str, Depends(oauth2)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """Dépendance : décode le Bearer token, charge l'utilisateur, ou 401."""
    refus = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "jeton invalide", {"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=[ALGO])
    except jwt.PyJWTError:
        raise refus from None
    user = session.exec(select(User).where(User.username == payload.get("sub"))).first()
    if user is None:
        raise refus
    return user


def assurer_admin(session: Session) -> None:
    """Crée le compte admin au premier démarrage s'il n'existe pas."""
    settings = get_settings()
    if not session.exec(select(User).where(User.username == settings.admin_user)).first():
        session.add(
            User(username=settings.admin_user, password_hash=hacher(settings.admin_password))
        )
        session.commit()
