# xmlrpc_serveur.py — Labo 16 : le service exposé en XML-RPC, version commentée.
#
# Rôle : le même service, en « appel de procédure à distance » avec des
#        enveloppes XML. XML-RPC (1998) est l'ancêtre direct de SOAP : même idée
#        (on appelle une FONCTION par son nom, les arguments sont sérialisés en
#        XML, tout passe en POST sur une seule URL), en beaucoup plus simple.
# Lancé par : python3 xmlrpc_serveur.py [port]
#
# Tout est dans la stdlib : xmlrpc.server côté serveur, xmlrpc.client côté client.

import sys
from xmlrpc.server import SimpleXMLRPCServer

import service


def creer_serveur(port: int = 0) -> SimpleXMLRPCServer:
    # allow_none : autorise None ↔ <nil/> (extension courante du protocole).
    # logRequests=False : silencieux.
    serveur = SimpleXMLRPCServer(("127.0.0.1", port), allow_none=True, logRequests=False)
    # On enregistre les fonctions Python sous un nom : c'est le « contrat ».
    # Le client appellera proxy.convertir(20) et proxy.status().
    serveur.register_function(service.convertir, "convertir")
    serveur.register_function(service.status, "status")
    # Introspection : le client peut demander system.listMethods() pour découvrir
    # ce qui existe. SOAP a la même idée, en beaucoup plus lourd : le WSDL.
    serveur.register_introspection_functions()
    return serveur


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    with creer_serveur(port) as serveur:
        print(f"XML-RPC sur http://127.0.0.1:{serveur.server_address[1]}/RPC2")
        serveur.serve_forever()
