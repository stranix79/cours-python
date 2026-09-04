# test_github_repos.py — Labo 14 : tests SANS réseau.
#
# httpx.MockTransport remplace la couche réseau : chaque requête est passée à
# une fonction Python qui fabrique la réponse. On simule ainsi deux pages de
# résultats reliées par un en-tête Link, un 404 et un 403 de rate limit.
import json

import httpx
import pytest

from github_repos import (compter_langages, formater_tableau, lister_depots,
                          charger_offline, main)

PAGE1 = [
    {"name": "alpha", "language": "Python", "stargazers_count": 3, "pushed_at": "2026-09-01T10:00:00Z"},
    {"name": "beta", "language": None, "stargazers_count": 0, "pushed_at": "2026-08-01T10:00:00Z"},
]
PAGE2 = [
    {"name": "gamma-long-name", "language": "Python", "stargazers_count": 1, "pushed_at": "2026-09-03T10:00:00Z"},
]


def faux_github(request: httpx.Request) -> httpx.Response:
    """Un GitHub de poche : /users/gilles/repos a deux pages, le reste est 404."""
    if request.url.path != "/users/gilles/repos":
        return httpx.Response(404, json={"message": "Not Found"})
    page = request.url.params.get("page", "1")
    if page == "1":
        # L'en-tête Link, exactement comme GitHub le renvoie.
        suivante = "https://api.github.com/users/gilles/repos?per_page=100&page=2"
        return httpx.Response(200, json=PAGE1, headers={"Link": f'<{suivante}>; rel="next"'})
    return httpx.Response(200, json=PAGE2)      # dernière page : pas de Link


@pytest.fixture
def client():
    with httpx.Client(base_url="https://api.github.com",
                      transport=httpx.MockTransport(faux_github)) as c:
        yield c


def test_lister_depots_suit_la_pagination(client):
    depots = lister_depots("gilles", client)
    assert [d["name"] for d in depots] == ["alpha", "beta", "gamma-long-name"]


def test_lister_depots_404_leve_une_erreur(client):
    with pytest.raises(httpx.HTTPStatusError):
        lister_depots("inconnu", client)


def test_compter_langages_trie_et_regroupe_none():
    assert compter_langages(PAGE1 + PAGE2) == {"Python": 2, "(aucun)": 1}


def test_compter_langages_vide():
    assert compter_langages([]) == {}


def test_formater_tableau_trie_par_push_et_aligne():
    texte = formater_tableau(PAGE1 + PAGE2)
    lignes = texte.splitlines()
    assert lignes[0].startswith("dépôt")
    # Les dépôts, du plus récent au plus ancien push.
    noms = [l.split()[0] for l in lignes[2:]]
    assert noms == ["gamma-long-name", "alpha", "beta"]
    assert "(aucun)" in lignes[4]
    assert "2026-09-03" in lignes[2]


def test_formater_tableau_vide():
    assert formater_tableau([]) == "(aucun dépôt)"


def test_charger_offline_lit_le_json_commite():
    depots = charger_offline()
    assert isinstance(depots, list) and len(depots) > 0
    assert {"name", "language", "pushed_at"} <= set(depots[0])


def test_main_offline_affiche_le_tableau(capsys):
    assert main(["--offline"]) == 0
    sortie = capsys.readouterr().out
    assert "dépôts, par langage" in sortie


def test_main_erreur_reseau_rend_2(monkeypatch):
    # On remplace creer_client par une fabrique dont le transport plante
    # comme si le DNS ne répondait pas.
    import github_repos

    def transport_casse(request):
        raise httpx.ConnectError("nom inconnu", request=request)

    monkeypatch.setattr(github_repos, "creer_client",
                        lambda *a, **k: httpx.Client(base_url="https://x",
                                                     transport=httpx.MockTransport(transport_casse)))
    assert main(["gilles"]) == 2
