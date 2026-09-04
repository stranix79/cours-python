# test_api.py — Labo 19 : tests de bout en bout avec TestClient et une base en mémoire.
# Lancer : pytest  (ou SOLUTION=1 pytest).

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db import get_session
from app.main import app, bootstrap_admin

ADMIN_PASSWORD = "admin-a-changer"   # la valeur par défaut de config.py


@pytest.fixture
def client():
    # Une base SQLite EN MÉMOIRE, neuve pour chaque test. StaticPool : une
    # seule connexion partagée, sinon chaque thread verrait une base vide
    # différente (":memory:" est par connexion).
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def session_de_test():
        with Session(engine) as session:
            yield session

    # Le lifespan de l'app (tables + admin) travaille sur l'engine de app/db.py,
    # pas sur le nôtre : on fait la même chose à la main, avec la même fonction.
    bootstrap_admin(engine)

    # dependency_overrides : partout où l'app demande get_session, elle
    # reçoit notre session de test. L'app ne touche jamais tickets.db.
    app.dependency_overrides[get_session] = session_de_test
    # Sans `with`, TestClient ne déclenche pas le lifespan : c'est voulu ici.
    yield TestClient(app)
    app.dependency_overrides.clear()


def token_de(client, username, password):
    r = client.post("/auth/token", data={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def gilles(client):
    assert client.post("/auth/register", json={"username": "gilles", "password": "motdepasse1"}).status_code == 201
    return token_de(client, "gilles", "motdepasse1")


@pytest.fixture
def admin(client):
    return token_de(client, "admin", ADMIN_PASSWORD)


def test_health_sans_auth(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert "X-Process-Time" in r.headers


def test_register_ne_renvoie_pas_le_hachage(client):
    r = client.post("/auth/register", json={"username": "gilles", "password": "motdepasse1"})
    assert r.status_code == 201
    assert r.json() == {"username": "gilles", "id": 2, "is_admin": False}   # id 1 = admin
    assert "hashed_password" not in r.json()


def test_register_doublon_409_et_mdp_court_422(client):
    client.post("/auth/register", json={"username": "gilles", "password": "motdepasse1"})
    assert client.post("/auth/register", json={"username": "gilles", "password": "autremotdepasse"}).status_code == 409
    assert client.post("/auth/register", json={"username": "bob", "password": "court"}).status_code == 422


def test_login_mauvais_mot_de_passe_401(client, gilles):
    r = client.post("/auth/token", data={"username": "gilles", "password": "faux"})
    assert r.status_code == 401
    assert r.headers["WWW-Authenticate"] == "Bearer"
    assert client.post("/auth/token", data={"username": "inconnu", "password": "faux"}).status_code == 401


def test_sans_jeton_401(client):
    assert client.get("/auth/me").status_code == 401
    assert client.get("/tickets").status_code == 401
    assert client.get("/tickets", headers={"Authorization": "Bearer n.importe.quoi"}).status_code == 401


def test_me(client, gilles):
    assert client.get("/auth/me", headers=gilles).json()["username"] == "gilles"


def test_creer_et_lister_ses_tickets(client, gilles):
    r = client.post("/tickets", json={"titre": "Disque plein", "severite": "haute"}, headers=gilles)
    assert r.status_code == 201
    t = r.json()
    assert t["owner_id"] == 2 and t["statut"] == "ouvert" and t["id"] == 1
    assert [x["titre"] for x in client.get("/tickets", headers=gilles).json()] == ["Disque plein"]


def test_isolation_entre_utilisateurs(client, gilles, admin):
    client.post("/tickets", json={"titre": "Ticket de Gilles"}, headers=gilles)
    client.post("/auth/register", json={"username": "bob", "password": "motdepasse2"})
    bob = token_de(client, "bob", "motdepasse2")
    client.post("/tickets", json={"titre": "Ticket de Bob"}, headers=bob)
    assert [t["titre"] for t in client.get("/tickets", headers=gilles).json()] == ["Ticket de Gilles"]
    assert [t["titre"] for t in client.get("/tickets", headers=bob).json()] == ["Ticket de Bob"]
    assert len(client.get("/tickets", headers=admin).json()) == 2        # l'admin voit tout
    assert client.get("/tickets/1", headers=bob).status_code == 404      # pas 403 : on ne révèle rien
    assert client.get("/tickets/1", headers=admin).status_code == 200


def test_patch_et_filtre_statut(client, gilles):
    client.post("/tickets", json={"titre": "Un ticket", "severite": "haute"}, headers=gilles)
    r = client.patch("/tickets/1", json={"statut": "resolu"}, headers=gilles)
    assert r.status_code == 200
    assert r.json()["statut"] == "resolu" and r.json()["severite"] == "haute"
    assert client.get("/tickets", params={"statut": "ouvert"}, headers=gilles).json() == []
    assert len(client.get("/tickets", params={"statut": "resolu"}, headers=gilles).json()) == 1


def test_supprimer_reserve_aux_admins(client, gilles, admin):
    client.post("/tickets", json={"titre": "À supprimer"}, headers=gilles)
    assert client.delete("/tickets/1").status_code == 401
    assert client.delete("/tickets/1", headers=gilles).status_code == 403
    assert client.delete("/tickets/1", headers=admin).status_code == 204
    assert client.delete("/tickets/1", headers=admin).status_code == 404


def test_pagination(client, gilles):
    for i in range(5):
        client.post("/tickets", json={"titre": f"Ticket numéro {i}"}, headers=gilles)
    page = client.get("/tickets", params={"offset": 2, "limit": 2}, headers=gilles).json()
    assert [t["id"] for t in page] == [3, 4]
    assert client.get("/tickets", params={"limit": 0}, headers=gilles).status_code == 422


def test_openapi_declare_la_securite(client):
    schema = client.get("/openapi.json").json()
    assert "OAuth2PasswordBearer" in schema["components"]["securitySchemes"]
