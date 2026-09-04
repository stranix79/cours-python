# test_srvctl.py — Labo 13 : tests de srvctl sans réseau ni vrai sous-processus.
# Lancé par : pytest   (squelette)   /   SOLUTION=1 pytest   (solution)
#
# Deux familles :
#   - les fonctions pures (charger_inventaire, filtrer, trouver, masquer) : appel direct ;
#   - l'application typer : typer.testing.CliRunner l'invoque en mémoire, capture
#     stdout et le code de sortie. subprocess.run est remplacé par un faux
#     (monkeypatch) pour que « ping » et « exec » ne lancent jamais rien.

import json
import subprocess

import pytest
from typer.testing import CliRunner

import srvctl

runner = CliRunner()


# --- fixtures ---------------------------------------------------------------

@pytest.fixture
def inventaire(tmp_path):
    """Un inventaire de test dans un dossier temporaire ; rend son chemin."""
    fichier = tmp_path / "inv.json"
    fichier.write_text(json.dumps({"serveurs": [
        {"nom": "web1", "hote": "10.0.0.1", "groupe": "web", "os": "debian12", "tags": ["nginx"]},
        {"nom": "db1", "hote": "10.0.0.2", "groupe": "db", "os": "ubuntu24", "tags": ["postgres", "critique"]},
    ]}), encoding="utf-8")
    return fichier


@pytest.fixture
def faux_run(monkeypatch):
    """Remplace subprocess.run par un faux qui enregistre les appels et rend un
    résultat contrôlé. Rend la liste des appels pour que le test puisse vérifier."""
    appels = []

    def run(commande, **kwargs):
        appels.append(commande)
        # ping vers 10.0.0.2 échoue, tout le reste réussit
        if commande[0] == "ping" and commande[-1] == "10.0.0.2":
            return subprocess.CompletedProcess(commande, 2, stdout="", stderr="Request timeout")
        return subprocess.CompletedProcess(commande, 0, stdout="ok\nround-trip 0.1 ms\n", stderr="")

    # srvctl fait « import subprocess » puis « subprocess.run(...) » : on patche
    # l'attribut du module subprocess, et srvctl le voit (chapitre 12.7).
    monkeypatch.setattr(subprocess, "run", run)
    return appels


# --- fonctions pures --------------------------------------------------------

def test_charger_inventaire(inventaire):
    serveurs = srvctl.charger_inventaire(inventaire)
    assert [s["nom"] for s in serveurs] == ["web1", "db1"]


def test_charger_inventaire_absent(tmp_path):
    with pytest.raises(FileNotFoundError):
        srvctl.charger_inventaire(tmp_path / "nexiste.json")


def test_charger_inventaire_sans_cle_serveurs(tmp_path):
    fichier = tmp_path / "inv.json"
    fichier.write_text('{"hosts": []}')
    with pytest.raises(ValueError, match="serveurs"):
        srvctl.charger_inventaire(fichier)


SERVEURS = [
    {"nom": "a", "hote": "1", "groupe": "web", "tags": ["nginx"]},
    {"nom": "b", "hote": "2", "groupe": "db", "tags": ["postgres", "critique"]},
    {"nom": "c", "hote": "3", "groupe": "web", "tags": []},
]


@pytest.mark.parametrize("groupe, tag, attendu", [
    (None, None, ["a", "b", "c"]),
    ("web", None, ["a", "c"]),
    (None, "critique", ["b"]),
    ("web", "nginx", ["a"]),
    ("ops", None, []),
])
def test_filtrer(groupe, tag, attendu):
    assert [s["nom"] for s in srvctl.filtrer(SERVEURS, groupe, tag)] == attendu


def test_trouver_nom_connu_et_hote_brut():
    assert srvctl.trouver(SERVEURS, "b") == "2"
    assert srvctl.trouver(SERVEURS, "192.168.1.1") == "192.168.1.1"


def test_masquer_filtre_et_cache():
    env = {"APP_ENV": "dev", "APP_TOKEN": "abc", "HOME": "/root", "DB_PASSWORD": "x"}
    assert srvctl.masquer(env, "APP_") == {"APP_ENV": "dev", "APP_TOKEN": "***"}
    assert srvctl.masquer(env)["DB_PASSWORD"] == "***"
    assert srvctl.masquer(env)["HOME"] == "/root"


# --- commande list ----------------------------------------------------------

def test_list_json(inventaire):
    r = runner.invoke(srvctl.app, ["-i", str(inventaire), "--json", "list", "-g", "db"])
    assert r.exit_code == 0, r.output
    donnees = json.loads(r.output)          # stdout doit être du JSON pur
    assert [s["nom"] for s in donnees] == ["db1"]


def test_list_tableau(inventaire):
    r = runner.invoke(srvctl.app, ["-i", str(inventaire), "list"])
    assert r.exit_code == 0
    assert "web1" in r.output and "db1" in r.output


def test_list_inventaire_absent(tmp_path):
    r = runner.invoke(srvctl.app, ["-i", str(tmp_path / "x.json"), "list"])
    assert r.exit_code == 1


# --- commande ping ----------------------------------------------------------

def test_ping_ok_et_ko(inventaire, faux_run):
    r = runner.invoke(srvctl.app, ["-i", str(inventaire), "--json", "ping", "web1", "db1"])
    assert r.exit_code == 1                 # db1 échoue → code 1
    resultats = json.loads(r.output)
    assert [x["ok"] for x in resultats] == [True, False]
    assert faux_run == [["ping", "-c", "1", "10.0.0.1"], ["ping", "-c", "1", "10.0.0.2"]]


def test_ping_all(inventaire, faux_run):
    r = runner.invoke(srvctl.app, ["-i", str(inventaire), "ping", "--all"])
    assert len(faux_run) == 2
    assert "OK" in r.output and "KO" in r.output


def test_ping_dry_run_ne_lance_rien(inventaire, faux_run):
    r = runner.invoke(srvctl.app, ["-i", str(inventaire), "--dry-run", "ping", "--all"])
    assert r.exit_code == 0
    assert faux_run == []                   # aucun subprocess.run


def test_ping_sans_cible(inventaire):
    r = runner.invoke(srvctl.app, ["-i", str(inventaire), "ping"])
    assert r.exit_code == 2


def test_ping_hote_timeout(monkeypatch):
    def run(commande, **kwargs):
        raise subprocess.TimeoutExpired(commande, kwargs.get("timeout"))
    monkeypatch.setattr(subprocess, "run", run)
    r = srvctl.ping_hote("10.0.0.9", timeout=0.5)
    assert r["ok"] is False and "timeout" in r["detail"]


# --- commande exec ----------------------------------------------------------

def test_exec_json(faux_run):
    r = runner.invoke(srvctl.app, ["--json", "exec", "--", "uname", "-s"])
    assert r.exit_code == 0
    assert json.loads(r.output)["stdout"].startswith("ok")
    assert faux_run == [["uname", "-s"]]


def test_exec_code_de_sortie_transmis(monkeypatch):
    monkeypatch.setattr(subprocess, "run",
                        lambda c, **k: subprocess.CompletedProcess(c, 3, stdout="", stderr="boum"))
    r = runner.invoke(srvctl.app, ["exec", "--", "faux"])
    assert r.exit_code == 3


def test_exec_dry_run(faux_run):
    r = runner.invoke(srvctl.app, ["--dry-run", "exec", "--", "rm", "-rf", "/"])
    assert r.exit_code == 0 and faux_run == []


# --- commande env -----------------------------------------------------------

def test_env_json_masque(monkeypatch):
    monkeypatch.setenv("LAB13_TOKEN", "secret")
    monkeypatch.setenv("LAB13_MODE", "test")
    r = runner.invoke(srvctl.app, ["--json", "env", "-p", "LAB13_"])
    assert r.exit_code == 0
    assert json.loads(r.output) == {"LAB13_MODE": "test", "LAB13_TOKEN": "***"}
