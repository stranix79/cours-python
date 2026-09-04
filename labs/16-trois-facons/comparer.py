# comparer.py — Labo 16 : les trois protocoles côte à côte, sur le fil.
#
# Rôle : lancer les trois serveurs dans des threads, envoyer à chacun la
#        requête « convertir 20 °C » avec un socket brut, et afficher les octets
#        exacts qui partent et qui reviennent. Pas de bibliothèque HTTP : on
#        voit ce que voit le réseau.
# Lancé par : python3 comparer.py

import json
import socket
import threading
import xmlrpc.client

import jsonrpc_serveur
import rest_serveur
import xmlrpc_serveur


def lancer_en_thread(serveur) -> int:
    """serve_forever() bloque : on le met dans un thread daemon (tué à la fin du programme)."""
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    return serveur.server_address[1]           # le port réellement choisi


def echange_brut(port: int, requete: bytes) -> bytes:
    """Envoie des octets, rend tous les octets reçus. HTTP/1.0 : le serveur ferme après la réponse."""
    with socket.create_connection(("127.0.0.1", port), timeout=5) as s:
        s.sendall(requete)
        reponse = b""
        while morceau := s.recv(4096):
            reponse += morceau
    return reponse


def requete_http(methode: str, chemin: str, corps: bytes = b"", content_type: str = "") -> bytes:
    """Assemble une requête HTTP/1.0 à la main : ligne de requête, en-têtes, ligne vide, corps."""
    lignes = [f"{methode} {chemin} HTTP/1.0", "Host: 127.0.0.1"]
    if corps:
        lignes += [f"Content-Type: {content_type}", f"Content-Length: {len(corps)}"]
    return ("\r\n".join(lignes) + "\r\n\r\n").encode() + corps


def afficher(titre: str, requete: bytes, reponse: bytes) -> None:
    print(f"\n{'=' * 70}\n{titre}\n{'=' * 70}")
    print(f"--- requête ({len(requete)} octets) ---")
    print(requete.decode())
    print(f"--- réponse ({len(reponse)} octets) ---")
    print(reponse.decode())


if __name__ == "__main__":
    p_rest = lancer_en_thread(rest_serveur.creer_serveur())
    p_xml = lancer_en_thread(xmlrpc_serveur.creer_serveur())
    p_json = lancer_en_thread(jsonrpc_serveur.creer_serveur())

    # 1. REST : la ressource est dans l'URL, l'argument dans la query string, pas de corps.
    req = requete_http("GET", "/convert?c=20")
    afficher("REST / JSON", req, echange_brut(p_rest, req))

    # 2. XML-RPC : POST sur une URL fixe, la fonction et ses arguments dans une enveloppe XML.
    #    xmlrpc.client.dumps fabrique exactement ce que ServerProxy enverrait.
    corps = xmlrpc.client.dumps((20,), methodname="convertir").encode()
    req = requete_http("POST", "/RPC2", corps, "text/xml")
    afficher("XML-RPC (l'ancêtre de SOAP)", req, echange_brut(p_xml, req))

    # 3. JSON-RPC : même idée, enveloppe JSON.
    corps = json.dumps({"jsonrpc": "2.0", "method": "convertir", "params": [20], "id": 1}).encode()
    req = requete_http("POST", "/", corps, "application/json")
    afficher("JSON-RPC 2.0", req, echange_brut(p_json, req))
