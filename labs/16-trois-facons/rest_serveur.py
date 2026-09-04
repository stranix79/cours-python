# rest_serveur.py — Labo 16 : le service exposé en REST/JSON.
#   GET /convert?c=20   → {"celsius": 20.0, "fahrenheit": 68.0, "kelvin": 293.15}
#   GET /status         → {"ok": true, ...}
#   /convert sans c ou c non numérique → 400 {"detail": "..."}
#   tout le reste       → 404 {"detail": "..."}
# Lancé par : python3 rest_serveur.py [port]   ou importé par comparer.py / les tests.

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import service


class GestionnaireREST(BaseHTTPRequestHandler):
    def envoyer_json(self, code: int, donnees: dict) -> None:
        """Statut, en-têtes, corps : le boulot répétitif d'une réponse HTTP."""
        corps = json.dumps(donnees).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)

    def do_GET(self) -> None:
        # self.path vaut par exemple "/convert?c=20".
        url = urlparse(self.path)              # url.path = "/convert", url.query = "c=20"
        params = parse_qs(url.query)           # {"c": ["20"]} (des listes !)
        # TODO : "/status" → envoyer_json(200, service.status())
        # TODO : "/convert" → si "c" absent : 400 ; sinon service.convertir(params["c"][0]),
        #        en attrapant ValueError → 400. Sinon 200 avec le résultat.
        # TODO : sinon 404 {"detail": ...}
        self.envoyer_json(501, {"detail": "TODO do_GET"})

    def log_message(self, format: str, *args) -> None:
        pass


def creer_serveur(port: int = 0) -> HTTPServer:
    """port=0 : le noyau choisit un port libre (pratique pour les tests)."""
    return HTTPServer(("127.0.0.1", port), GestionnaireREST)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    with creer_serveur(port) as serveur:
        print(f"REST sur http://127.0.0.1:{serveur.server_address[1]}/convert?c=20")
        serveur.serve_forever()
