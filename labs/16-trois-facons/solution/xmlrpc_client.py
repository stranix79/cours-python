# xmlrpc_client.py — Labo 16 : appeler le service XML-RPC (stdlib).
# Lancé par : python3 xmlrpc_client.py [port]
import sys
import xmlrpc.client


def convertir(port: int, celsius: float) -> dict:
    # ServerProxy fabrique un objet dont CHAQUE attribut devient un appel distant :
    # proxy.convertir(20) → POST /RPC2 avec <methodCall><methodName>convertir...
    # C'est l'illusion de l'appel local ; le « stub » que SOAP génère depuis le WSDL.
    with xmlrpc.client.ServerProxy(f"http://127.0.0.1:{port}/RPC2") as proxy:
        return proxy.convertir(celsius)


def status(port: int) -> dict:
    with xmlrpc.client.ServerProxy(f"http://127.0.0.1:{port}/RPC2") as proxy:
        return proxy.status()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    with xmlrpc.client.ServerProxy(f"http://127.0.0.1:{port}/RPC2") as proxy:
        print(proxy.system.listMethods())       # découverte : quelles fonctions existent ?
        print(proxy.convertir(20))
        print(proxy.status())
        try:
            proxy.inexistante()
        except xmlrpc.client.Fault as e:        # l'erreur distante devient une exception locale
            print("Fault :", e.faultCode, e.faultString)
