# jsonrpc_client.py — Labo 16 : appeler le service JSON-RPC (stdlib).
# Lancé par : python3 jsonrpc_client.py [port]
import itertools
import json
import sys
from urllib.request import Request, urlopen

_ids = itertools.count(1)       # chaque requête a un id : la réponse le renvoie, pour les apparier


def appeler(port: int, methode: str, *params) -> dict:
    """Un appel JSON-RPC : POST d'une enveloppe, lecture de l'enveloppe de réponse."""
    enveloppe = {"jsonrpc": "2.0", "method": methode, "params": list(params), "id": next(_ids)}
    req = Request(f"http://127.0.0.1:{port}/", data=json.dumps(enveloppe).encode(),
                  headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=5) as resp:
        reponse = json.load(resp)
    if "error" in reponse:
        # Comme xmlrpc.client.Fault : l'erreur distante devient une exception locale.
        raise RuntimeError(f"{reponse['error']['code']} : {reponse['error']['message']}")
    return reponse["result"]


def convertir(port: int, celsius: float) -> dict:
    return appeler(port, "convertir", celsius)


def status(port: int) -> dict:
    return appeler(port, "status")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8003
    print(convertir(port, 20))
    print(status(port))
    try:
        appeler(port, "inexistante")
    except RuntimeError as e:
        print("erreur :", e)
