# inventaire_sqlite.py — Labo 18 (partie a) : inventaire de serveurs avec sqlite3, SQL à la main.
# Deux tables : serveurs, et services (un service appartient à un serveur : colonne serveur_id).

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS serveurs (
    id  INTEGER PRIMARY KEY,
    nom TEXT    NOT NULL UNIQUE,
    ip  TEXT    NOT NULL,
    os  TEXT    NOT NULL,
    cpu INTEGER NOT NULL DEFAULT 1
);
-- TODO : la table services : id, serveur_id (REFERENCES serveurs(id) ON DELETE CASCADE),
--        nom TEXT, port INTEGER. Et un index sur serveur_id.
"""


def ouvrir(chemin: str | Path = "inventaire.db") -> sqlite3.Connection:
    """Ouvre (ou crée) la base et s'assure que les tables existent."""
    con = sqlite3.connect(chemin)
    con.row_factory = sqlite3.Row            # row["nom"] au lieu de row[1]
    con.execute("PRAGMA foreign_keys = ON")  # sinon SQLite ignore les clés étrangères
    con.executescript(SCHEMA)
    return con


def ajouter_serveur(con: sqlite3.Connection, nom: str, ip: str, os: str, cpu: int = 1) -> int:
    """Insère un serveur et renvoie son id."""
    cur = con.execute(
        "INSERT INTO serveurs (nom, ip, os, cpu) VALUES (?, ?, ?, ?)",   # des ?, JAMAIS une f-string
        (nom, ip, os, cpu),
    )
    con.commit()
    return cur.lastrowid


def ajouter_service(con: sqlite3.Connection, serveur_id: int, nom: str, port: int) -> int:
    # TODO : INSERT dans services, commit, renvoyer cur.lastrowid
    raise NotImplementedError("TODO")


def serveurs_par_os(con: sqlite3.Connection, os: str) -> list[dict]:
    """Tous les serveurs d'un OS donné, triés par nom, sous forme de dicts."""
    # TODO : SELECT * ... WHERE os = ? ORDER BY nom ; fetchall() ; [dict(r) for r in rows]
    raise NotImplementedError("TODO")


def services_de(con: sqlite3.Connection, nom_serveur: str) -> list[dict]:
    """Les services d'un serveur (dicts {"nom", "port"}), triés par port.
    On part du NOM du serveur : il faut une jointure services JOIN serveurs."""
    # TODO : SELECT services.nom, services.port FROM services JOIN serveurs ON ... WHERE serveurs.nom = ?
    raise NotImplementedError("TODO")


def ports_ouverts(con: sqlite3.Connection) -> list[tuple[str, int]]:
    """(nom du serveur, port) pour tout l'inventaire, trié par nom puis port."""
    # TODO : même jointure, sans WHERE
    raise NotImplementedError("TODO")


def changer_cpu(con: sqlite3.Connection, nom: str, cpu: int) -> bool:
    """Renvoie True si un serveur a été modifié."""
    # TODO : UPDATE ... ; cur.rowcount dit combien de lignes ont été touchées.
    #   `with con:` fait le commit à la sortie du bloc.
    raise NotImplementedError("TODO")


def supprimer_serveur(con: sqlite3.Connection, nom: str) -> bool:
    # TODO : DELETE ; grâce à ON DELETE CASCADE, les services partent avec.
    raise NotImplementedError("TODO")


if __name__ == "__main__":
    con = ouvrir(":memory:")   # base en mémoire : disparaît à la fermeture
    web = ajouter_serveur(con, "web-01", "10.0.0.11", "debian", cpu=4)
    print("web-01 a l'id", web)
    # TODO : ajoute des services, affiche services_de(con, "web-01") et ports_ouverts(con)
    con.close()
