# test_dispo.py — Labo 15 : tests des trois stratégies, SANS réseau.
#
# httpx.MockTransport joue le serveur : il marche aussi bien pour httpx.Client
# (sync) que pour httpx.AsyncClient. Les tests `async def` tournent grâce à
# pytest-asyncio (asyncio_mode = auto dans pytest.ini).
import asyncio
from pathlib import Path

import httpx
import pytest

from dispo import (Resultat, lire_urls, verifier, verifier_sequentiel, verifier_threads,
                   verifier_async, verifier_tout_async, formater)

URLS = ["http://x/ok", "http://x/erreur", "http://x/panne", "http://x/ok2"]


def faux_serveur(request: httpx.Request) -> httpx.Response:
    """/ok → 200, /erreur → 500, /panne → comme si la connexion était refusée."""
    if request.url.path == "/panne":
        raise httpx.ConnectError("connexion refusée", request=request)
    if request.url.path == "/erreur":
        return httpx.Response(500)
    return httpx.Response(200)


@pytest.fixture
def client():
    with httpx.Client(transport=httpx.MockTransport(faux_serveur)) as c:
        yield c


@pytest.fixture
async def client_async():
    async with httpx.AsyncClient(transport=httpx.MockTransport(faux_serveur)) as c:
        yield c


def verifie_resultats(resultats: list[Resultat]) -> None:
    """Le contrat commun aux trois stratégies : même ordre, même contenu."""
    assert [r.url for r in resultats] == URLS               # l'ordre des URLs est conservé
    assert [r.statut for r in resultats] == [200, 500, None, 200]
    assert [r.ok for r in resultats] == [True, False, False, True]
    assert resultats[2].erreur == "ConnectError"
    assert all(r.duree >= 0 for r in resultats)


def test_lire_urls_ignore_commentaires_et_vides(tmp_path: Path):
    f = tmp_path / "urls.txt"
    f.write_text("# commentaire\nhttp://a/\n\n  http://b/  \n", encoding="utf-8")
    assert lire_urls(f) == ["http://a/", "http://b/"]


def test_verifier_ne_leve_jamais(client):
    assert verifier(client, "http://x/panne").statut is None
    assert verifier(client, "http://x/ok").ok


def test_sequentiel(client):
    verifie_resultats(verifier_sequentiel(URLS, client))


def test_threads(client):
    verifie_resultats(verifier_threads(URLS, client, limite=2))


async def test_verifier_async(client_async):
    r = await verifier_async(client_async, "http://x/ok", asyncio.Semaphore(1))
    assert r.statut == 200


async def test_tout_async(client_async):
    verifie_resultats(await verifier_tout_async(URLS, client_async, limite=2))


async def test_le_semaphore_borne_la_concurrence():
    """Avec limite=2, jamais plus de deux requêtes « en vol » en même temps."""
    en_vol = 0
    maximum = 0

    async def serveur_compteur(request: httpx.Request) -> httpx.Response:
        nonlocal en_vol, maximum
        en_vol += 1
        maximum = max(maximum, en_vol)
        await asyncio.sleep(0.01)                            # simule le réseau
        en_vol -= 1
        return httpx.Response(200)

    async with httpx.AsyncClient(transport=httpx.MockTransport(serveur_compteur)) as c:
        await verifier_tout_async([f"http://x/{i}" for i in range(10)], c, limite=2)
    assert maximum == 2


def test_formater():
    texte = formater([Resultat("http://a/", 200, 0.1), Resultat("http://b/", None, 5.0, "ReadTimeout")])
    assert texte.splitlines()[-1] == "1/2 disponibles"
    assert "ReadTimeout" in texte
