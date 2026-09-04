# rest_serveur.py — Labo 16 : le service exposé en REST/JSON, version commentée.
#
# Rôle : un serveur HTTP (stdlib) avec deux ressources :
#   GET /convert?c=20   → {"celsius": 20.0, "fahrenheit": 68.0, "kelvin": 293.15}
#   GET /status         → {"ok": true, ...}
#   tout le reste       → 404 {"detail": "..."}
# Lancé par : python3 rest_serveur.py [port]   ou importé par comparer.py / les tests.
#
# En REST, l'URL désigne la RESSOURCE, la méthode HTTP dit l'ACTION, le code
# de statut dit comment ça s'est passé, et le corps est une représentation
# (ici JSON). C'est exactement ce que FastAPI fera pour nous au chapitre 17,
# avec dix fois moins de lignes.

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import service


class GestionnaireREST(BaseHTTPRequestHandler):
    def envoyer_json(self, code: int, donnees: dict) -> None:
        """Le boulot répétitif d'une réponse HTTP : statut, en-têtes, corps."""
        corps = json.dumps(donnees).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")   # dit au client comment lire le corps
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)

    def do_GET(self) -> None:
        # self.path = "/convert?c=20". urlparse sépare chemin et query string,
        # parse_qs transforme "c=20&x=1" en {"c": ["20"], "x": ["1"]} (des listes :
        # un paramètre peut être répété).
        url = urlparse(self.path)
        params = parse_qs(url.query)

        if url.path == "/status":
            self.envoyer_json(200, service.status())
        elif url.path == "/convert":
            if "c" not in params:
                # 400 : c'est le CLIENT qui s'est trompé (paramètre manquant)
                self.envoyer_json(400, {"detail": "paramètre c manquant"})
                return
            try:
                self.envoyer_json(200, service.convertir(params["c"][0]))
            except ValueError:
                self.envoyer_json(400, {"detail": f"c doit être un nombre, pas {params['c'][0]!r}"})
        else:
            self.envoyer_json(404, {"detail": f"pas de ressource {url.path}"})

    def log_message(self, format: str, *args) -> None:
        pass    # silencieux ; enlève cette méthode pour voir une ligne par requête


def creer_serveur(port: int = 0) -> HTTPServer:
    """port=0 : le noyau choisit un port libre (pratique pour les tests)."""
    return HTTPServer(("127.0.0.1", port), GestionnaireREST)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    with creer_serveur(port) as serveur:
        print(f"REST sur http://127.0.0.1:{serveur.server_address[1]}/convert?c=20")
        serveur.serve_forever()
