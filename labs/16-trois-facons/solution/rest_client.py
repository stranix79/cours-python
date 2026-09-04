# rest_client.py — Labo 16 : appeler le service REST avec urllib (stdlib).
# Lancé par : python3 rest_client.py [port]
import json
import sys
from urllib.error import HTTPError
from urllib.request import urlopen


def convertir(port: int, celsius: float) -> dict:
    # L'appel REST : un GET sur l'URL de la ressource, avec le paramètre dans la query string.
    with urlopen(f"http://127.0.0.1:{port}/convert?c={celsius}", timeout=5) as resp:
        return json.load(resp)


def status(port: int) -> dict:
    with urlopen(f"http://127.0.0.1:{port}/status", timeout=5) as resp:
        return json.load(resp)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    print(convertir(port, 20))
    print(status(port))
    try:
        urlopen(f"http://127.0.0.1:{port}/inconnu", timeout=5)
    except HTTPError as e:                     # urllib lève sur 4xx/5xx
        print(e.code, json.load(e))            # 404 {'detail': 'pas de ressource /inconnu'}
