# app/routers/auth.py — Labo 19 : inscription, login (jeton), profil.
#
# Branché par main.py sous /auth.

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from ..deps import CurrentUser, SessionDep
from ..models import Token, User, UserCreate, UserPublic
from ..security import creer_token, hacher, verifier

router = APIRouter(prefix="/auth", tags=["auth"])


# response_model=UserPublic : on renvoie l'objet User complet, FastAPI ne
# laisse passer que les champs de UserPublic. Le hashed_password reste en base.
@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(donnees: UserCreate, session: SessionDep) -> User:
    if session.exec(select(User).where(User.username == donnees.username)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce nom est déjà pris")
    user = User(username=donnees.username, hashed_password=hacher(donnees.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# OAuth2PasswordRequestForm : le standard OAuth2 « password flow » envoie un
# FORMULAIRE (username=...&password=...), pas du JSON. C'est ce que Swagger UI
# envoie quand tu cliques sur Authorize, d'où python-multipart dans les dépendances.
@router.post("/token", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep) -> Token:
    user = session.exec(select(User).where(User.username == form.username)).first()
    # Même message que l'utilisateur existe ou non : on ne révèle pas quels
    # comptes existent. verifier() est appelé seulement si user existe, mais
    # bcrypt reste suffisamment lent pour ne pas trahir grand-chose.
    if user is None or not verifier(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=creer_token(user.username))


@router.get("/me", response_model=UserPublic)
def me(user: CurrentUser) -> User:
    # Toute la logique est dans la dépendance : pas de jeton valide, pas d'appel.
    return user
