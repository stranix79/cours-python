# jsonrpc_serveur.py — Labo 16 : le service exposé en JSON-RPC 2.0, écrit à la main.
#
# Requête  : {"jsonrpc": "2.0", "method": "convertir", "params": [20], "id": 1}
# Réponse  : {"jsonrpc": "2.0", "result": {...}, "id": 1}
# Erreur   : {"jsonrpc": "2.0", "error": {"code": -32601, "message": "..."}, "id": 1}
# Spécification (une page) : https://www.jsonrpc.org/specification
# Lancé par : python3 jsonrpc_serveur.py [port]

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

import service

METHODES = {
    "convertir": service.convertir,
    "status": service.status,
}

PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS = -32700, -32600, -32601, -32602


def erreur(code: int, message: str, id_) -> dict:
    return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": id_}


def traiter(requete: dict) -> dict:
    """Exécute UNE requête JSON-RPC et fabrique la réponse. Pas de HTTP ici : testable seul."""
    id_ = requete.get("id")
    # TODO : si requete.get("jsonrpc") != "2.0" ou pas de "method" → erreur(INVALID_REQUEST, ...)
    # TODO : fonction = METHODES.get(...) ; None → erreur(METHOD_NOT_FOUND, ...)
    # TODO : params = requete.get("params", []) ; liste → fonction(*params), dict → fonction(**params)
    #        TypeError ou ValueError → erreur(INVALID_PARAMS, str(e))
    # TODO : sinon {"jsonrpc": "2.0", "result": ..., "id": id_}
    return erreur(-32603, "TODO traiter", id_)


class GestionnaireJSONRPC(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        # TODO : lire le corps : taille = int(self.headers.get("Content-Length", 0)),
        #        brut = self.rfile.read(taille). (Sans taille, read() attendrait la fin de connexion.)
        # TODO : json.loads(brut) → traiter(...) ; JSONDecodeError → erreur(PARSE_ERROR, ..., None)
        # TODO : répondre 200 (TOUJOURS 200 en RPC : l'erreur est dans l'enveloppe),
        #        Content-Type application/json, Content-Length, corps.
        corps = json.dumps(erreur(-32603, "TODO do_POST", None)).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)

    def log_message(self, format: str, *args) -> None:
        pass


def creer_serveur(port: int = 0) -> HTTPServer:
    return HTTPServer(("127.0.0.1", port), GestionnaireJSONRPC)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8003
    with creer_serveur(port) as serveur:
        print(f"JSON-RPC sur http://127.0.0.1:{serveur.server_address[1]}/")
        serveur.serve_forever()
