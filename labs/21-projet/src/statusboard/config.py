# src/statusboard/config.py — Labo 21 : la configuration, lue dans l'environnement (jalon 1).
"""Configuration par variables d'environnement, préfixe STATUSBOARD_."""

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///statusboard.db"
    secret_key: str = "change-moi-en-prod-0123456789abcdef"
    token_minutes: int = 60
    interval_s: float = 30.0
    worker_enabled: bool = True
    admin_user: str = "admin"
    admin_password: str = "admin"


@lru_cache
def get_settings() -> Settings:
    # TODO : lire STATUSBOARD_DATABASE_URL, STATUSBOARD_SECRET_KEY, STATUSBOARD_TOKEN_MINUTES,
    #        STATUSBOARD_INTERVAL_S, STATUSBOARD_WORKER ("1"/"0"), STATUSBOARD_ADMIN_USER,
    #        STATUSBOARD_ADMIN_PASSWORD, avec les défauts de Settings (os.environ.get).
    return Settings(database_url=os.environ.get("STATUSBOARD_DATABASE_URL", Settings.database_url))
