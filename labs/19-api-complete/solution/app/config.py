# app/config.py — Labo 19 : la configuration, lue dans les variables d'environnement.
#
# Utilisé par : db.py, security.py, main.py, routers/auth.py.
#
# Règle DevOps : rien de spécifique à un environnement (secret, URL de base,
# durée des jetons) n'est écrit dans le code. Tout vient de l'environnement,
# comme le veut la « 12-factor app ». pydantic-settings lit les variables
# d'environnement (et un fichier .env s'il existe), les valide et les convertit.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Chaque attribut = une variable d'environnement, préfixée par TICKETS_ :
    # TICKETS_SECRET_KEY, TICKETS_DATABASE_URL... La valeur par défaut sert en
    # développement ; en production, on la surcharge (et le secret par défaut
    # ne doit JAMAIS survivre à un déploiement).
    model_config = SettingsConfigDict(env_prefix="TICKETS_", env_file=".env", extra="ignore")

    # Au moins 32 octets pour HS256 (PyJWT avertit en dessous). En prod :
    #   python3 -c "import secrets; print(secrets.token_hex(32))"
    secret_key: str = "dev-secret-a-changer-en-prod-0123456789abcdef"
    database_url: str = "sqlite:///tickets.db"
    token_minutes: int = 60
    admin_password: str = "admin-a-changer"   # mot de passe du compte admin créé au démarrage
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()
