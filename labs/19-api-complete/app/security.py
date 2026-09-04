# app/security.py — Labo 19 : mots de passe et jetons JWT.
#
# Utilisé par : routers/auth.py (hacher, vérifier, créer un jeton) et deps.py (décoder).

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt  # le paquet PyJWT

from .config import settings

ALGORITHME = "HS256"   # HMAC-SHA256 : signature symétrique avec notre secret


def hacher(mot_de_passe: str) -> str:
    """Renvoie le hachage bcrypt (avec son sel) à stocker en base.
    bcrypt est LENT exprès (≈ 100 ms) : un attaquant qui vole la base ne peut
    tester que quelques mots de passe par seconde, contre des milliards avec md5."""
    # bcrypt travaille sur des bytes ; gensalt() génère un sel aléatoire, donc
    # deux utilisateurs avec le même mot de passe ont des hachages différents.
    return bcrypt.hashpw(mot_de_passe.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verifier(mot_de_passe: str, hachage: str) -> bool:
    """Compare un mot de passe en clair au hachage stocké, en temps constant."""
    return bcrypt.checkpw(mot_de_passe.encode("utf-8"), hachage.encode("utf-8"))


def creer_token(sujet: str, minutes: int | None = None) -> str:
    """Fabrique un JWT signé. `sub` (subject) = l'identité, `exp` = l'expiration.
    Le contenu est seulement encodé en base64, PAS chiffré : n'y mets rien de secret."""
    # TODO : expiration = maintenant (UTC) + timedelta(minutes=minutes or settings.token_minutes)
    #        payload = {"sub": sujet, "exp": expiration}
    #        return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHME)
    raise NotImplementedError("TODO")


def decoder_token(token: str) -> str | None:
    """Renvoie le `sub` si la signature est bonne et le jeton non expiré, sinon None."""
    # TODO : jwt.decode(token, settings.secret_key, algorithms=[ALGORITHME]) dans un try ;
    #        toute jwt.PyJWTError (signature, expiration, format) → None ; sinon payload["sub"]
    raise NotImplementedError("TODO")
