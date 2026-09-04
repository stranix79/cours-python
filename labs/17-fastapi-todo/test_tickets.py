# test_tickets.py — Labo 17 : tests de l'API avec TestClient (aucun serveur à lancer).
# Lancer : pytest  (ou SOLUTION=1 pytest pour vérifier la solution).

import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app


@pytest.fixture
def client():
    # Chaque test repart d'un stockage vide : les tests ne dépendent pas de l'ordre.
    store.vider()
    return TestClient(app)


def test_racine_et_health(client):
    assert client.get("/").status_code == 200
    assert client.get("/health").json() == {"status": "ok"}


def test_creer_renvoie_201_et_le_ticket(client):
    r = client.post("/tickets", json={"titre": "Disque plein", "severite": "haute"})
    assert r.status_code == 201
    corps = r.json()
    assert corps["id"] == 1
    assert corps["titre"] == "Disque plein"
    assert corps["severite"] == "haute"
    assert corps["statut"] == "ouvert"
    assert "cree_le" in corps


def test_titre_trop_court_donne_422(client):
    r = client.post("/tickets", json={"titre": "ab"})
    assert r.status_code == 422
    # Le détail dit quel champ pose problème.
    assert r.json()["detail"][0]["loc"] == ["body", "titre"]


def test_severite_inconnue_donne_422(client):
    r = client.post("/tickets", json={"titre": "Réseau HS", "severite": "apocalyptique"})
    assert r.status_code == 422


def test_lire_et_404(client):
    cree = client.post("/tickets", json={"titre": "Réseau HS"}).json()
    assert client.get(f"/tickets/{cree['id']}").json()["titre"] == "Réseau HS"
    assert client.get("/tickets/999").status_code == 404
    assert client.get("/tickets/abc").status_code == 422  # pas un int


def test_lister_et_filtrer(client):
    client.post("/tickets", json={"titre": "Premier", "severite": "basse"})
    client.post("/tickets", json={"titre": "Deuxième", "severite": "haute"})
    client.post("/tickets", json={"titre": "Troisième", "severite": "haute"})
    assert len(client.get("/tickets").json()) == 3
    hautes = client.get("/tickets", params={"severite": "haute"}).json()
    assert [t["titre"] for t in hautes] == ["Deuxième", "Troisième"]
    assert len(client.get("/tickets", params={"limite": 2}).json()) == 2
    assert client.get("/tickets", params={"limite": 0}).status_code == 422


def test_patch_ne_touche_que_les_champs_envoyes(client):
    cree = client.post("/tickets", json={"titre": "Premier", "severite": "haute"}).json()
    r = client.patch(f"/tickets/{cree['id']}", json={"statut": "resolu"})
    assert r.status_code == 200
    assert r.json()["statut"] == "resolu"
    assert r.json()["severite"] == "haute"  # inchangé
    assert r.json()["titre"] == "Premier"


def test_put_remplace_tout(client):
    cree = client.post("/tickets", json={"titre": "Premier", "description": "bla", "severite": "haute"}).json()
    r = client.put(f"/tickets/{cree['id']}", json={"titre": "Nouveau titre"})
    assert r.status_code == 200
    corps = r.json()
    assert corps["titre"] == "Nouveau titre"
    assert corps["description"] == ""          # revenu à la valeur par défaut
    assert corps["severite"] == "moyenne"      # idem
    assert corps["id"] == cree["id"]
    assert corps["cree_le"] == cree["cree_le"]  # conservé


def test_supprimer(client):
    cree = client.post("/tickets", json={"titre": "Premier"}).json()
    assert client.delete(f"/tickets/{cree['id']}").status_code == 204
    assert client.get(f"/tickets/{cree['id']}").status_code == 404
    assert client.delete(f"/tickets/{cree['id']}").status_code == 404


def test_openapi_expose_les_routes(client):
    schema = client.get("/openapi.json").json()
    assert "/tickets/{ticket_id}" in schema["paths"]
    assert set(schema["paths"]["/tickets/{ticket_id}"]) == {"get", "put", "patch", "delete"}
