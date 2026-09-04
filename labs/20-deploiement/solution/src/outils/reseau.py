# src/outils/reseau.py — Labo 20 (solution) : fonctions réseau, nettoyées.
#
# Rôle : validation d'adresses IP, découpage d'URL, test de port TCP, masques.
# Utilisé par : outils.cli, tests/test_reseau.py.
"""Utilitaires réseau : IP, URL, ports, masques."""

import ipaddress
import socket
from urllib.parse import urlparse


def est_ip_valide(s: str) -> bool:
    try:
        ipaddress.ip_address(s)
    except ValueError:
        # `except:` nu (E722) attrapait aussi KeyboardInterrupt et SystemExit :
        # on attrape exactement ce que ip_address lève sur une entrée invalide.
        return False
    return True


def est_privee(s: str) -> bool:
    return ipaddress.ip_address(s).is_private


def decouper_url(url: str) -> tuple[str, str | None, int, str]:
    """(scheme, hôte, port, chemin) avec le port par défaut du scheme si absent."""
    p = urlparse(url)
    # urlparse renvoie port=None s'il n'est pas écrit : on le remplace, et le
    # type de retour dit `int`, pas `int | None`, parce qu'on garantit une valeur.
    port = p.port
    if port is None:
        port = 443 if p.scheme == "https" else 80
    return (p.scheme, p.hostname, port, p.path or "/")


def port_ouvert(hote: str, port: int, timeout: float = 1.0) -> bool:
    """True si une connexion TCP à hote:port aboutit dans le délai."""
    # Le `with` ferme la socket dans tous les cas : c'est le try/finally
    # d'origine, en une ligne (chapitre 11).
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((hote, port))
        except OSError:
            return False
    return True


def masque_vers_prefixe(masque: str) -> int:
    """'255.255.255.0' → 24."""
    return ipaddress.IPv4Network(f"0.0.0.0/{masque}").prefixlen
