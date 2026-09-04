# src/statusboard/config.py — Labo 21 (solution) : la configuration, lue dans l'environnement.
#
# Rôle : un seul endroit où l'application lit ses variables d'environnement
# (12 facteurs, chapitre 20). Tout le reste appelle get_settings().
# Utilisé par : db.py, auth.py, worker.py, api.py, tests/conftest.py.
"""Configuration par variables d'environnement, préfixe STATUSBOARD_."""

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///statusboard.db"
    secret_key: str = "change-moi-en-prod-0123456789abcdef"  # signe les JWT ; un secret réel vient de l'env
    token_minutes: int = 60  # durée de vie d'un jeton
    interval_s: float = 30.0  # cadence par défaut des vérifications
    worker_enabled: bool = True  # False dans les tests : on pilote à la main
    admin_user: str = "admin"  # compte créé au premier démarrage
    admin_password: str = "admin"


@lru_cache  # lu une fois, puis mémorisé
def get_settings() -> Settings:
    env = os.environ.get  # raccourci : env("X", "défaut")
    return Settings(
        database_url=env("STATUSBOARD_DATABASE_URL", Settings.database_url),
        secret_key=env("STATUSBOARD_SECRET_KEY", Settings.secret_key),
        token_minutes=int(env("STATUSBOARD_TOKEN_MINUTES", "60")),
        interval_s=float(env("STATUSBOARD_INTERVAL_S", "30")),
        worker_enabled=env("STATUSBOARD_WORKER", "1") == "1",
        admin_user=env("STATUSBOARD_ADMIN_USER", Settings.admin_user),
        admin_password=env("STATUSBOARD_ADMIN_PASSWORD", Settings.admin_password),
    )
