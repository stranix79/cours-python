# outils/reseau.py — Labo 06 : retry et test de port TCP.
# Importé par outils/__init__.py et outils/cli.py.

import socket
import time


def retry(fonction, *args, essais: int = 3, attente: float = 0.0, **kwargs):
    """Appelle fonction(*args, **kwargs) jusqu'à réussite, au plus `essais` fois."""
    # TODO : reprends ta version du labo 05
    raise NotImplementedError("TODO")


def port_ouvert(host: str, port: int, timeout: float = 1.0) -> bool:
    """True si une connexion TCP vers host:port aboutit dans le délai."""
    # TODO : socket.create_connection((host, port), timeout=timeout) renvoie
    #        une socket connectée (à fermer : with ... as s:) ou lève OSError.
    #        try / except OSError : return False.
    raise NotImplementedError("TODO")
