# jsonrpc_serveur.py — Labo 16 : le service exposé en JSON-RPC 2.0, version commentée.
#
# Rôle : même idée que XML-RPC (on appelle une fonction par son nom sur une
#        seule URL en POST), mais l'enveloppe est du JSON. Le protocole tient en
#        une page : https://www.jsonrpc.org/specification . On l'implémente à la
#        main en quarante lignes ; c'est ce que parlent LSP (les serveurs de
#        langage de VS Code), Ethereum, et pas mal d'outils internes.
#
# Requête  : {"jsonrpc": "2.0", "method": "convertir", "params": [20], "id": 1}
# Réponse  : {"jsonrpc": "2.0", "result": {...}, "id": 1}
# Erreur   : {"jsonrpc": "2.0", "error": {"code": -32601, "message": "..."}, "id": 1}
# Lancé par : python3 jsonrpc_serveur.py [port]

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

import service

# Le registre des méthodes exposées : nom → fonction Python.
METHODES = {
    "convertir": service.convertir,
    "status": service.status,
}

# Codes d'erreur standard de la spécification.
PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS = -32700, -32600, -32601, -32602


def traiter(requete: dict) -> dict:
    """Exécute UNE requête JSON-RPC et fabrique la réponse. Pur : pas de HTTP ici."""
    id_ = requete.get("id")
    if requete.get("jsonrpc") != "2.0" or "method" not in requete:
        return {"jsonrpc": "2.0", "error": {"code": INVALID_REQUEST, "message": "requête invalide"}, "id": id_}
    fonction = METHODES.get(requete["method"])
    if fonction is None:
        return {"jsonrpc": "2.0", "error": {"code": METHOD_NOT_FOUND, "message": f"méthode inconnue : {requete['method']}"}, "id": id_}
    params = requete.get("params", [])
    try:
        # params peut être une liste (positionnels) ou un dict (nommés) : la spec autorise les deux.
        resultat = fonction(**params) if isinstance(params, dict) else fonction(*params)
    except (TypeError, ValueError) as e:
        return {"jsonrpc": "2.0", "error": {"code": INVALID_PARAMS, "message": str(e)}, "id": id_}
    return {"jsonrpc": "2.0", "result": resultat, "id": id_}


class GestionnaireJSONRPC(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        # Le corps arrive dans self.rfile ; sa taille est dans Content-Length.
        # Sans cette lecture bornée, rfile.read() attendrait la fin de connexion.
        taille = int(self.headers.get("Content-Length", 0))
        brut = self.rfile.read(taille)
        try:
            reponse = traiter(json.loads(brut))
        except json.JSONDecodeError:
            reponse = {"jsonrpc": "2.0", "error": {"code": PARSE_ERROR, "message": "JSON illisible"}, "id": None}
        corps = json.dumps(reponse).encode("utf-8")
        # Toujours 200 : en RPC, l'erreur est DANS l'enveloppe, pas dans le code HTTP.
        # C'est une différence de philosophie avec REST, où le code HTTP porte le sens.
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
