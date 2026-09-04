# tests/test_api.py — Labo 21 (solution) : l'API de bout en bout avec TestClient.
from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    assert client.get("/health").json()["status"] == "ok"


def test_creer_exige_un_jeton(client: TestClient) -> None:
    r = client.post("/targets", json={"name": "x", "kind": "tcp", "address": "127.0.0.1:1"})
    assert r.status_code == 401


def test_mauvais_mot_de_passe(client: TestClient) -> None:
    assert client.post("/token", data={"username": "admin", "password": "nope"}).status_code == 401


def test_cycle_complet(client: TestClient, auth: dict[str, str], serveur_local: str) -> None:
    # Créer
    r = client.post(
        "/targets",
        json={"name": "local", "kind": "http", "address": f"{serveur_local}/ok"},
        headers=auth,
    )
    assert r.status_code == 201, r.text
    tid = r.json()["id"]
    # Doublon → 409
    doublon = {"name": "local", "kind": "http", "address": "x"}
    assert client.post("/targets", json=doublon, headers=auth).status_code == 409
    # Jamais vérifiée : ok = None
    assert client.get("/status").json()[0]["ok"] is None
    # Vérification à la demande
    c = client.post(f"/targets/{tid}/check", headers=auth).json()
    assert c["ok"] is True and c["detail"] == "HTTP 200"
    # Historique et état
    assert len(client.get(f"/targets/{tid}/checks").json()) == 1
    etat = client.get("/status").json()[0]
    assert etat["ok"] is True and etat["target"]["name"] == "local"
    # Supprimer
    assert client.delete(f"/targets/{tid}", headers=auth).status_code == 204
    assert client.get("/targets").json() == []


def test_sse_envoie_un_instantane(
    client: TestClient, auth: dict[str, str], serveur_local: str
) -> None:
    client.post(
        "/targets",
        json={"name": "sse", "kind": "http", "address": f"{serveur_local}/ok"},
        headers=auth,
    )
    # TestClient attend la FIN de la réponse : sans limit=0 le flux est infini
    # et le test ne rendrait jamais la main. Pour voir des événements en direct,
    # lance l'API et `curl -N /events`.
    r = client.get("/events", params={"limit": 0})
    assert r.headers["content-type"].startswith("text/event-stream")
    lignes = r.text.splitlines()
    assert lignes[0] == "event: snapshot"
    assert lignes[1].startswith("data: ") and '"name": "sse"' in lignes[1]
