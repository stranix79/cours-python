# service.py — Labo 16 : LE service, indépendant de tout protocole.
#
# Rôle : les deux fonctions métier que les trois serveurs (REST, XML-RPC,
#        JSON-RPC) exposent. Aucune notion de HTTP ici : c'est le point du
#        labo. Le « web service », c'est ça + une façon de l'appeler à distance.
# Importé par : rest_serveur.py, xmlrpc_serveur.py, jsonrpc_serveur.py, les tests.

import platform
import time

DEMARRAGE = time.time()


def convertir(celsius: float) -> dict:
    """Convertit des degrés Celsius en Fahrenheit et Kelvin."""
    c = float(celsius)
    return {"celsius": c, "fahrenheit": round(c * 9 / 5 + 32, 2), "kelvin": round(c + 273.15, 2)}


def status() -> dict:
    """Quelques infos sur le serveur : le « /health » que toute API finit par avoir."""
    return {
        "ok": True,
        "hote": platform.node(),
        "python": platform.python_version(),
        "uptime_s": round(time.time() - DEMARRAGE, 1),
    }
