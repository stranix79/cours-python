# test_trois_facons.py — Labo 16 : chaque serveur est lancé dans un thread sur
# un port libre (port 0), puis appelé avec son client. Aucun port en dur,
# aucun serveur à lancer à la main.
import json
import threading
import xmlrpc.client
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

import jsonrpc_client
import jsonrpc_serveur
import rest_client
import rest_serveur
import service
import xmlrpc_client
import xmlrpc_serveur


def demarrer(serveur) -> int:
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    return serveur.server_address[1]


# scope="module" : un serveur par fichier de test, pas un par test.
@pytest.fixture(scope="module")
def port_rest():
    serveur = rest_serveur.creer_serveur()
    yield demarrer(serveur)
    serveur.shutdown()


@pytest.fixture(scope="module")
def port_xml():
    serveur = xmlrpc_serveur.creer_serveur()
    yield demarrer(serveur)
    serveur.shutdown()


@pytest.fixture(scope="module")
def port_json():
    serveur = jsonrpc_serveur.creer_serveur()
    yield demarrer(serveur)
    serveur.shutdown()


ATTENDU_20 = {"celsius": 20.0, "fahrenheit": 68.0, "kelvin": 293.15}


def test_service_pur():
    assert service.convertir(20) == ATTENDU_20
    assert service.convertir("-40")["fahrenheit"] == -40.0
    assert service.status()["ok"] is True


# --- REST ---------------------------------------------------------------------

def test_rest_convert(port_rest):
    assert rest_client.convertir(port_rest, 20) == ATTENDU_20


def test_rest_status(port_rest):
    assert rest_client.status(port_rest)["ok"] is True


def test_rest_404_et_400(port_rest):
    with pytest.raises(HTTPError) as exc:
        urlopen(f"http://127.0.0.1:{port_rest}/inconnu", timeout=5)
    assert exc.value.code == 404
    assert "detail" in json.load(exc.value)
    with pytest.raises(HTTPError) as exc:
        urlopen(f"http://127.0.0.1:{port_rest}/convert", timeout=5)          # c manquant
    assert exc.value.code == 400
    with pytest.raises(HTTPError) as exc:
        urlopen(f"http://127.0.0.1:{port_rest}/convert?c=chaud", timeout=5)  # pas un nombre
    assert exc.value.code == 400


def test_rest_content_type(port_rest):
    with urlopen(f"http://127.0.0.1:{port_rest}/status", timeout=5) as resp:
        assert resp.headers["Content-Type"] == "application/json"


# --- XML-RPC ------------------------------------------------------------------

def test_xmlrpc_convert(port_xml):
    assert xmlrpc_client.convertir(port_xml, 20) == ATTENDU_20


def test_xmlrpc_introspection_et_fault(port_xml):
    with xmlrpc.client.ServerProxy(f"http://127.0.0.1:{port_xml}/RPC2") as proxy:
        assert {"convertir", "status"} <= set(proxy.system.listMethods())
        with pytest.raises(xmlrpc.client.Fault):
            proxy.inexistante()


# --- JSON-RPC -----------------------------------------------------------------

def test_jsonrpc_convert(port_json):
    assert jsonrpc_client.convertir(port_json, 20) == ATTENDU_20


def test_jsonrpc_erreurs(port_json):
    with pytest.raises(RuntimeError, match="-32601"):
        jsonrpc_client.appeler(port_json, "inexistante")
    with pytest.raises(RuntimeError, match="-32602"):
        jsonrpc_client.appeler(port_json, "convertir", "chaud")


def test_jsonrpc_traiter_est_pur():
    """La logique RPC se teste sans serveur du tout."""
    rep = jsonrpc_serveur.traiter({"jsonrpc": "2.0", "method": "convertir", "params": {"celsius": 0}, "id": 7})
    assert rep == {"jsonrpc": "2.0", "result": {"celsius": 0.0, "fahrenheit": 32.0, "kelvin": 273.15}, "id": 7}
    assert jsonrpc_serveur.traiter({"method": "x"})["error"]["code"] == -32600
