# app/db.py — Labo 19 : l'engine SQLModel et la dépendance « une session par requête ».
#
# Utilisé par : main.py (création des tables au démarrage), deps.py et les routeurs
# via Depends(get_session).

from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from .config import settings

# SQLite refuse par défaut qu'une connexion soit utilisée depuis un autre
# thread que celui qui l'a créée. FastAPI exécute les routes `def` dans un
# pool de threads : on désactive cette vérification (SQLModel gère le reste).
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)


def create_db_and_tables(moteur=engine) -> None:
    """Crée les tables manquantes. Le paramètre permet aux tests de passer
    leur propre engine (base en mémoire)."""
    # Importer les modèles ici garantit qu'ils sont déclarés avant create_all.
    from . import models  # noqa: F401

    SQLModel.metadata.create_all(moteur)


def get_session() -> Iterator[Session]:
    """Dépendance FastAPI : ouvre une session pour la durée d'une requête.
    Le `yield` (chapitre 11) : ce qui est avant s'exécute avant la route,
    ce qui est après s'exécute après la réponse, même en cas d'erreur.
    C'est exactement un context manager, et c'est la garantie que la session
    est toujours fermée."""
    with Session(engine) as session:
        yield session
