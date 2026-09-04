# outils/reseau.py — Labo 06 (solution) : retry et test de port TCP.
# Importé par outils/__init__.py et outils/cli.py.

import socket
import time


def retry(fonction, *args, essais: int = 3, attente: float = 0.0, **kwargs):
    """Appelle fonction(*args, **kwargs) jusqu'à réussite, au plus `essais` fois.

    Relance la dernière exception si tout échoue. Repris du labo 05.
    """
    derniere_erreur: Exception | None = None
    for numero in range(1, essais + 1):
        try:
            return fonction(*args, **kwargs)
        except Exception as e:
            derniere_erreur = e
            if numero < essais and attente > 0:
                time.sleep(attente)
    assert derniere_erreur is not None
    raise derniere_erreur


def port_ouvert(host: str, port: int, timeout: float = 1.0) -> bool:
    """True si une connexion TCP vers host:port aboutit dans le délai.

    C'est un `nc -z host port` en Python. On n'envoie rien : le simple
    handshake TCP suffit à savoir que quelqu'un écoute.
    """
    try:
        # create_connection fait la résolution DNS + connect(). Le `with`
        # garantit la fermeture de la socket, même si on sort par exception.
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        # OSError couvre tout : refus de connexion, timeout (socket.timeout en
        # est une sous-classe), hôte inconnu (socket.gaierror aussi).
        return False
