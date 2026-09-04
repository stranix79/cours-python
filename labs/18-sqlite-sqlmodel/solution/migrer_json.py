# migrer_json.py — Labo 18 : charge un inventaire JSON (le format du labo 07) dans
# la base SQLite via SQLModel.
#
# Usage : python3 migrer_json.py serveurs.json [inventaire.db]
# Utilise : inventaire_sqlmodel.py.

import json
import sys
from pathlib import Path

from sqlmodel import Session, select

from inventaire_sqlmodel import Serveur, Service, creer_engine


def migrer(chemin_json: Path, url_db: str) -> int:
    """Insère chaque serveur du JSON (avec ses services) ; renvoie le nombre insérés.
    Un serveur déjà présent (même nom) est ignoré : le script est relançable."""
    donnees = json.loads(chemin_json.read_text(encoding="utf-8"))
    engine = creer_engine(url_db)
    inseres = 0
    with Session(engine) as session:
        for entree in donnees:
            existe = session.exec(select(Serveur).where(Serveur.nom == entree["nom"])).first()
            if existe:
                continue
            # On construit le serveur ET ses services en objets Python, on
            # n'ajoute que le serveur : les services suivent par la Relationship.
            serveur = Serveur(nom=entree["nom"], ip=entree["ip"], os=entree["os"], cpu=entree.get("cpu", 1))
            serveur.services = [Service(nom=s["nom"], port=s["port"]) for s in entree.get("services", [])]
            session.add(serveur)
            inseres += 1
        # Un seul commit pour tout le lot : soit tout passe, soit rien
        # (une transaction), et c'est bien plus rapide qu'un commit par ligne.
        session.commit()
    return inseres


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage : migrer_json.py serveurs.json [inventaire.db]")
    fichier = Path(sys.argv[1])
    db = sys.argv[2] if len(sys.argv) > 2 else "inventaire.db"
    n = migrer(fichier, f"sqlite:///{db}")
    print(f"{n} serveur(s) importé(s) dans {db}")
