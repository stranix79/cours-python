# test_inventaire.py — Labo 18 : les mêmes tests pour les deux implémentations.
# Lancer : pytest  (ou SOLUTION=1 pytest).

from pathlib import Path

import pytest
from sqlmodel import Session

import inventaire_sqlite as sq
import inventaire_sqlmodel as sm
from migrer_json import migrer

ICI = Path(__file__).parent


# ---------- partie a : sqlite3 ----------

@pytest.fixture
def con(tmp_path):
    # tmp_path : un dossier temporaire fourni par pytest, détruit après le test.
    # On teste donc sur une vraie base fichier, sans polluer le dossier du labo.
    con = sq.ouvrir(tmp_path / "test.db")
    yield con
    con.close()


def _peupler_sqlite(con):
    web = sq.ajouter_serveur(con, "web-01", "10.0.0.11", "debian", cpu=4)
    sq.ajouter_service(con, web, "nginx", 443)
    sq.ajouter_service(con, web, "sshd", 22)
    db = sq.ajouter_serveur(con, "db-01", "10.0.0.21", "ubuntu", cpu=16)
    sq.ajouter_service(con, db, "postgres", 5432)


def test_sqlite_ajouter_et_lister_par_os(con):
    _peupler_sqlite(con)
    debian = sq.serveurs_par_os(con, "debian")
    assert [s["nom"] for s in debian] == ["web-01"]
    assert debian[0]["cpu"] == 4
    assert sq.serveurs_par_os(con, "freebsd") == []


def test_sqlite_nom_unique(con):
    sq.ajouter_serveur(con, "web-01", "10.0.0.11", "debian")
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        sq.ajouter_serveur(con, "web-01", "10.0.0.99", "debian")


def test_sqlite_jointure(con):
    _peupler_sqlite(con)
    assert sq.services_de(con, "web-01") == [{"nom": "sshd", "port": 22}, {"nom": "nginx", "port": 443}]
    assert sq.services_de(con, "inconnu") == []
    assert sq.ports_ouverts(con) == [("db-01", 5432), ("web-01", 22), ("web-01", 443)]


def test_sqlite_injection_impossible(con):
    _peupler_sqlite(con)
    # Avec une f-string, ce « nom » renverrait tous les serveurs. Avec des
    # paramètres, il est cherché tel quel et n'existe pas.
    assert sq.services_de(con, "x' OR '1'='1") == []


def test_sqlite_update_et_delete_en_cascade(con):
    _peupler_sqlite(con)
    assert sq.changer_cpu(con, "web-01", 8) is True
    assert sq.changer_cpu(con, "inconnu", 8) is False
    assert sq.serveurs_par_os(con, "debian")[0]["cpu"] == 8
    assert sq.supprimer_serveur(con, "web-01") is True
    assert sq.services_de(con, "web-01") == []
    assert sq.ports_ouverts(con) == [("db-01", 5432)]


# ---------- partie b : SQLModel ----------

@pytest.fixture
def session():
    # "sqlite://" : base en mémoire, neuve pour chaque test, rien à nettoyer.
    engine = sm.creer_engine("sqlite://")
    with Session(engine) as session:
        yield session


def _peupler_sqlmodel(session):
    web = sm.ajouter_serveur(session, "web-01", "10.0.0.11", "debian", cpu=4)
    sm.ajouter_service(session, web, "nginx", 443)
    sm.ajouter_service(session, web, "sshd", 22)
    db = sm.ajouter_serveur(session, "db-01", "10.0.0.21", "ubuntu", cpu=16)
    sm.ajouter_service(session, db, "postgres", 5432)


def test_sqlmodel_ajouter_donne_un_id(session):
    s = sm.ajouter_serveur(session, "web-01", "10.0.0.11", "debian")
    assert s.id == 1
    assert isinstance(s, sm.Serveur)


def test_sqlmodel_lister_par_os(session):
    _peupler_sqlmodel(session)
    assert [s.nom for s in sm.serveurs_par_os(session, "debian")] == ["web-01"]
    assert sm.serveurs_par_os(session, "freebsd") == []


def test_sqlmodel_relation(session):
    _peupler_sqlmodel(session)
    services = sm.services_de(session, "web-01")
    assert [(s.nom, s.port) for s in services] == [("sshd", 22), ("nginx", 443)]
    assert services[0].serveur.nom == "web-01"      # la relation dans l'autre sens
    assert sm.services_de(session, "inconnu") == []
    assert sm.ports_ouverts(session) == [("db-01", 5432), ("web-01", 22), ("web-01", 443)]


def test_sqlmodel_update_et_delete(session):
    _peupler_sqlmodel(session)
    assert sm.changer_cpu(session, "web-01", 8) is True
    assert sm.serveurs_par_os(session, "debian")[0].cpu == 8
    assert sm.supprimer_serveur(session, "web-01") is True
    assert sm.supprimer_serveur(session, "web-01") is False
    assert sm.ports_ouverts(session) == [("db-01", 5432)]


# ---------- migration ----------

def test_migration_json(tmp_path):
    url = f"sqlite:///{tmp_path / 'inv.db'}"
    assert migrer(ICI / "serveurs.json", url) == 4
    assert migrer(ICI / "serveurs.json", url) == 0     # relançable : rien en double
    with Session(sm.creer_engine(url)) as session:
        assert len(sm.ports_ouverts(session)) == 7
        assert [s.nom for s in sm.serveurs_par_os(session, "debian")] == ["web-01", "web-02"]
