# inventaire.py — Labo 07 : inventaire de machines persisté en JSON, export CSV.
# Usage : python3 inventaire.py <commande> [arguments]   (voir USAGE ci-dessous)

import csv
import json
import sys
from pathlib import Path

# Path(__file__).parent = le dossier où est CE fichier, quel que soit le dossier
# d'où on lance le script. Sans ça, `data/` serait créé dans le dossier courant.
DOSSIER = Path(__file__).parent / "data"
FICHIER = DOSSIER / "inventaire.json"

USAGE = """usage : inventaire.py <commande> [arguments]

  ajouter   <nom> <ip> <role> [port ...]
  lister
  chercher  <texte>
  supprimer <nom>
  exporter  <fichier.csv>
  importer  <fichier.csv>
"""


def charger() -> list[dict]:
    """Lit data/inventaire.json ; liste vide si le fichier n'existe pas."""
    # TODO : if not FICHIER.exists(): return []
    #        with open(FICHIER, encoding="utf-8") as f: return json.load(f)
    raise NotImplementedError("TODO")


def sauver(machines: list[dict]) -> None:
    """Écrit la liste dans data/inventaire.json (crée data/ au besoin)."""
    # TODO : DOSSIER.mkdir(parents=True, exist_ok=True)
    #        json.dump(machines, f, indent=2, ensure_ascii=False)
    #        Bonus : écrire dans FICHIER.with_suffix(".json.tmp") puis .replace(FICHIER)
    raise NotImplementedError("TODO")


def trouver(machines: list[dict], nom: str) -> dict | None:
    """La machine qui porte ce nom, ou None."""
    for m in machines:
        if m["nom"] == nom:
            return m
    return None


def cmd_ajouter(args: list[str]) -> None:
    # TODO : nom, ip, role = args[0], args[1], args[2] ; ports = [int(p) for p in args[3:]]
    #        refuse si trouver(...) n'est pas None ; sinon append + sauver
    raise NotImplementedError("TODO")


def cmd_lister(args: list[str]) -> None:
    # TODO : en-tête puis une ligne alignée par machine :
    #        f"{m['nom']:<10} {m['ip']:<16} {m['role']:<10} {', '.join(map(str, m['ports']))}"
    raise NotImplementedError("TODO")


def cmd_chercher(args: list[str]) -> None:
    # TODO : texte = args[0].lower() ; affiche les machines dont nom, ip ou role
    #        contient texte (str.lower() des deux côtés)
    raise NotImplementedError("TODO")


def cmd_supprimer(args: list[str]) -> None:
    # TODO : reconstruis la liste sans la machine (compréhension), sauve,
    #        affiche "supprimé" ou "introuvable"
    raise NotImplementedError("TODO")


def cmd_exporter(args: list[str]) -> None:
    # TODO : csv.DictWriter(f, fieldnames=["nom", "ip", "role", "ports"]) ;
    #        ports → ";".join(map(str, ports)). N'oublie pas newline="".
    raise NotImplementedError("TODO")


def cmd_importer(args: list[str]) -> None:
    # TODO : csv.DictReader ; ports = [int(p) for p in ligne["ports"].split(";") if p]
    #        n'ajoute que les noms absents ; compte importées / déjà présentes
    raise NotImplementedError("TODO")


COMMANDES = {
    "ajouter": cmd_ajouter,
    "lister": cmd_lister,
    "chercher": cmd_chercher,
    "supprimer": cmd_supprimer,
    "exporter": cmd_exporter,
    "importer": cmd_importer,
}


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] not in COMMANDES:
        print(USAGE, file=sys.stderr)
        sys.exit(1)
    try:
        COMMANDES[args[0]](args[1:])
    except (IndexError, ValueError) as e:
        print(f"arguments invalides : {e}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
