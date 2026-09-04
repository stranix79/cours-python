# tests/conftest.py — Labo 21 (solution) : fixtures partagées.
#
# Rôle : une base SQLite temporaire, le worker désactivé, un serveur HTTP local
# à surveiller, et un TestClient déjà authentifié.
# Lu par : pytest, avant tous les tests du dossier.
import os
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

# Ces variables doivent être posées AVANT le premier import de statusboard :
# get_settings() est mémorisé (lru_cache) au premier appel.
os.environ["STATUSBOARD_DATABASE_URL"] = "sqlite://"  # en mémoire
os.environ["STATUSBOARD_WORKER"] = "0"  # on pilote les ticks à la main
os.environ["STATUSBOARD_SECRET_KEY"] = "secret-de-test-assez-long-pour-hs256-0123456789"

from fastapi.testclient import TestClient  # noqa: E402

from statusboard.api import app  # noqa: E402
from statusboard.db import get_engine  # noqa: E402


class _Handler(BaseHTTPRequestHandler):
    """Répond 200 sur /ok, 500 sur /ko, et se tait dans le terminal."""

    def do_GET(self) -> None:
        code = 200 if self.path == "/ok" else 500
        self.send_response(code)
        self.end_headers()
        self.wfile.write(b"salut")

    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture(scope="session")
def serveur_local() -> Iterator[str]:
    """Un vrai serveur HTTP dans un thread, sur un port libre : la cible des tests."""
    srv = HTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


@pytest.fixture
def client() -> Iterator[TestClient]:
    # `with` déclenche le lifespan (tables + admin) ; sqlite:// en mémoire avec
    # un StaticPool par défaut : tous les accès voient la même base.
    with TestClient(app) as c:
        yield c
    # Base propre entre deux tests : on vide les tables.
    from sqlmodel import SQLModel

    SQLModel.metadata.drop_all(get_engine())


@pytest.fixture
def token(client: TestClient) -> str:
    r = client.post("/token", data={"username": "admin", "password": "admin"})
    assert r.status_code == 200, r.text
    return str(r.json()["access_token"])


@pytest.fixture
def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
