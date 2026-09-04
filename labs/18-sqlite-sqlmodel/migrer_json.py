# migrer_json.py — Labo 18 : importe serveurs.json (format du labo 07) dans SQLite via SQLModel.
# Usage : python3 migrer_json.py serveurs.json [inventaire.db]

import json
import sys
from pathlib import Path

from sqlmodel import Session, select

from inventaire_sqlmodel import Serveur, Service, creer_engine


def migrer(chemin_json: Path, url_db: str) -> int:
    """Insère chaque serveur (et ses services) ; renvoie le nombre insérés.
    Un serveur déjà présent (même nom) est ignoré : le script doit être relançable."""
    donnees = json.loads(chemin_json.read_text(encoding="utf-8"))
    engine = creer_engine(url_db)
    inseres = 0
    with Session(engine) as session:
        for entree in donnees:
            # TODO : si un Serveur de ce nom existe déjà → continue
            # TODO : construis le Serveur, puis serveur.services = [Service(...) for ...]
            #        session.add(serveur) suffit : les services suivent par la relation
            inseres += 1
        session.commit()   # un seul commit pour tout le lot
    return inseres


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage : migrer_json.py serveurs.json [inventaire.db]")
    fichier = Path(sys.argv[1])
    db = sys.argv[2] if len(sys.argv) > 2 else "inventaire.db"
    print(f"{migrer(fichier, f'sqlite:///{db}')} serveur(s) importé(s) dans {db}")
