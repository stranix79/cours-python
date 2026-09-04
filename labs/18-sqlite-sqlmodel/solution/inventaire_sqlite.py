# inventaire_sqlite.py — Labo 18 (partie a) : un inventaire de serveurs avec le module
# sqlite3 de la bibliothèque standard, en SQL écrit à la main.
#
# Utilisé par : test_inventaire.py, et lançable directement (python3 inventaire_sqlite.py).
#
# Deux tables : serveurs, et services (chaque service appartient à un serveur :
# c'est une relation « un à plusieurs », matérialisée par la colonne serveur_id).

import sqlite3
from pathlib import Path

# Les ordres de création. IF NOT EXISTS rend le script relançable.
# REFERENCES serveurs(id) est la clé étrangère : un service pointe vers un serveur.
# ON DELETE CASCADE : supprimer un serveur supprime ses services (SQLite ne
# l'applique que si PRAGMA foreign_keys = ON, voir ouvrir()).
SCHEMA = """
CREATE TABLE IF NOT EXISTS serveurs (
    id  INTEGER PRIMARY KEY,
    nom TEXT    NOT NULL UNIQUE,
    ip  TEXT    NOT NULL,
    os  TEXT    NOT NULL,
    cpu INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS services (
    id         INTEGER PRIMARY KEY,
    serveur_id INTEGER NOT NULL REFERENCES serveurs(id) ON DELETE CASCADE,
    nom        TEXT    NOT NULL,
    port       INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_services_serveur ON services(serveur_id);
"""


def ouvrir(chemin: str | Path = "inventaire.db") -> sqlite3.Connection:
    """Ouvre (ou crée) la base et s'assure que les tables existent."""
    con = sqlite3.connect(chemin)
    # Par défaut, une ligne est un tuple : row[0], row[1]... Avec sqlite3.Row,
    # on peut écrire row["nom"], et dict(row) pour la convertir.
    con.row_factory = sqlite3.Row
    # SQLite n'applique PAS les clés étrangères par défaut (héritage historique).
    con.execute("PRAGMA foreign_keys = ON")
    # executescript exécute plusieurs ordres séparés par des ; (execute n'en accepte qu'un).
    con.executescript(SCHEMA)
    return con


def ajouter_serveur(con: sqlite3.Connection, nom: str, ip: str, os: str, cpu: int = 1) -> int:
    """Insère un serveur et renvoie son id."""
    # Les ? sont des PARAMÈTRES : sqlite3 les substitue lui-même, en échappant
    # ce qu'il faut. JAMAIS de f-string pour construire du SQL avec des données
    # venues de l'extérieur : c'est la porte ouverte à l'injection SQL.
    cur = con.execute(
        "INSERT INTO serveurs (nom, ip, os, cpu) VALUES (?, ?, ?, ?)",
        (nom, ip, os, cpu),
    )
    con.commit()  # sans commit, la transaction reste ouverte et rien n'est écrit sur disque
    # lastrowid : l'id auto-attribué par INTEGER PRIMARY KEY.
    return cur.lastrowid


def ajouter_service(con: sqlite3.Connection, serveur_id: int, nom: str, port: int) -> int:
    cur = con.execute(
        "INSERT INTO services (serveur_id, nom, port) VALUES (?, ?, ?)",
        (serveur_id, nom, port),
    )
    con.commit()
    return cur.lastrowid


def serveurs_par_os(con: sqlite3.Connection, os: str) -> list[dict]:
    """Tous les serveurs d'un OS donné, triés par nom."""
    rows = con.execute("SELECT * FROM serveurs WHERE os = ? ORDER BY nom", (os,)).fetchall()
    return [dict(r) for r in rows]


def services_de(con: sqlite3.Connection, nom_serveur: str) -> list[dict]:
    """Les services d'un serveur, via une jointure : on part du nom du serveur,
    pas de son id, donc il faut relier les deux tables."""
    rows = con.execute(
        """
        SELECT services.nom, services.port
        FROM services
        JOIN serveurs ON serveurs.id = services.serveur_id
        WHERE serveurs.nom = ?
        ORDER BY services.port
        """,
        (nom_serveur,),
    ).fetchall()
    return [dict(r) for r in rows]


def ports_ouverts(con: sqlite3.Connection) -> list[tuple[str, int]]:
    """(serveur, port) pour tout l'inventaire : la requête typique d'un audit."""
    rows = con.execute(
        "SELECT serveurs.nom, services.port FROM services "
        "JOIN serveurs ON serveurs.id = services.serveur_id ORDER BY 1, 2"
    ).fetchall()
    return [(r["nom"], r["port"]) for r in rows]


def changer_cpu(con: sqlite3.Connection, nom: str, cpu: int) -> bool:
    """Renvoie True si un serveur a été modifié."""
    # `with con:` ouvre une transaction et fait commit à la sortie (ou rollback
    # si une exception est levée dedans). Ça ne ferme PAS la connexion.
    with con:
        cur = con.execute("UPDATE serveurs SET cpu = ? WHERE nom = ?", (cpu, nom))
    return cur.rowcount == 1


def supprimer_serveur(con: sqlite3.Connection, nom: str) -> bool:
    with con:
        cur = con.execute("DELETE FROM serveurs WHERE nom = ?", (nom,))
    return cur.rowcount == 1


if __name__ == "__main__":
    # Petite démo sur une base en mémoire : ":memory:" crée une base qui
    # disparaît à la fermeture. Parfait pour essayer.
    con = ouvrir(":memory:")
    web = ajouter_serveur(con, "web-01", "10.0.0.11", "debian", cpu=4)
    ajouter_service(con, web, "nginx", 443)
    ajouter_service(con, web, "sshd", 22)
    db = ajouter_serveur(con, "db-01", "10.0.0.21", "ubuntu", cpu=16)
    ajouter_service(con, db, "postgres", 5432)
    print("debian :", [s["nom"] for s in serveurs_par_os(con, "debian")])
    print("services de web-01 :", services_de(con, "web-01"))
    print("ports :", ports_ouverts(con))
    supprimer_serveur(con, "web-01")
    print("après suppression, services restants :", con.execute("SELECT count(*) FROM services").fetchone()[0])
    con.close()
