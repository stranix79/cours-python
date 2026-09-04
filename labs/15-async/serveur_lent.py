# serveur_lent.py — Labo 15 : un serveur HTTP local qui répond lentement.
#
# Rôle : simuler vingt sites plus ou moins lents pour travailler hors ligne
#        et avoir des mesures reproductibles. Bibliothèque standard seulement.
# Lancé par : python3 serveur_lent.py [port]   (dans un second terminal)
#
# Routes :
#   /                → 200 après 0,2 à 0,8 s (aléatoire, mais fixé par l'URL)
#   /site/<n>        → idem, chaque n a son propre délai stable
#   /erreur          → 500 immédiat
#   /timeout         → ne répond jamais (dort 30 s)
#
# ThreadingHTTPServer traite chaque connexion dans un thread : si le serveur
# était mono-thread, un client asynchrone qui envoie 20 requêtes d'un coup
# les verrait quand même servies une par une, et la démo n'aurait aucun sens.

import random
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Gestionnaire(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/erreur":
            self.send_error(500, "Panne simulée")
            return
        if self.path == "/timeout":
            time.sleep(30)
            return
        # Un délai reproductible : le même chemin donne toujours le même délai.
        delai = random.Random(self.path).uniform(0.2, 0.8)
        time.sleep(delai)
        corps = f"OK {self.path} en {delai:.2f} s\n".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)

    def log_message(self, format: str, *args) -> None:
        pass        # silence : sinon une ligne par requête dans le terminal


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    with ThreadingHTTPServer(("127.0.0.1", port), Gestionnaire) as serveur:
        print(f"serveur lent sur http://127.0.0.1:{port}  (Ctrl-C pour arrêter)")
        try:
            serveur.serve_forever()
        except KeyboardInterrupt:
            print("\narrêt")
