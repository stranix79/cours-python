# tests/test_checks.py — Labo 21 (solution) : les vérifications, contre le serveur local.
import pytest

from statusboard.checks import check_http, check_tcp


@pytest.mark.asyncio
async def test_http_ok(serveur_local: str) -> None:
    c = await check_http(f"{serveur_local}/ok")
    assert c.ok and c.detail == "HTTP 200" and c.latency_ms is not None


@pytest.mark.asyncio
async def test_http_erreur_serveur(serveur_local: str) -> None:
    c = await check_http(f"{serveur_local}/ko")
    assert not c.ok and c.detail == "HTTP 500"


@pytest.mark.asyncio
async def test_http_injoignable() -> None:
    c = await check_http("http://127.0.0.1:1/")  # rien n'écoute sur le port 1
    assert not c.ok and c.detail == "ConnectError"


@pytest.mark.asyncio
async def test_tcp(serveur_local: str) -> None:
    port = int(serveur_local.rsplit(":", 1)[1])
    assert (await check_tcp("127.0.0.1", port)).ok
    assert not (await check_tcp("127.0.0.1", 1)).ok
