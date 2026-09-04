# xmlrpc_serveur.py — Labo 16 : le service exposé en XML-RPC (l'ancêtre de SOAP).
# Lancé par : python3 xmlrpc_serveur.py [port]
# Le client appellera proxy.convertir(20), proxy.status() et proxy.system.listMethods().

import sys
from xmlrpc.server import SimpleXMLRPCServer

import service


def creer_serveur(port: int = 0) -> SimpleXMLRPCServer:
    # TODO : SimpleXMLRPCServer(("127.0.0.1", port), allow_none=True, logRequests=False)
    # TODO : register_function(service.convertir, "convertir") et idem pour status
    # TODO : register_introspection_functions() pour system.listMethods()
    raise NotImplementedError("TODO creer_serveur")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    with creer_serveur(port) as serveur:
        print(f"XML-RPC sur http://127.0.0.1:{serveur.server_address[1]}/RPC2")
        serveur.serve_forever()
