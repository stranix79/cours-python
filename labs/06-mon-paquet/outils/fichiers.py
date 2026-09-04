# outils/fichiers.py — Labo 06 : tailles de fichiers et de dossiers.
# Importé par outils/__init__.py et outils/cli.py.

from pathlib import Path

UNITES = ("o", "Ko", "Mo", "Go", "To")


def taille_lisible(octets: int, decimales: int = 1) -> str:
    """1536 → '1.5 Ko'."""
    # TODO : reprends ta version du labo 05
    raise NotImplementedError("TODO")


def taille_dossier(chemin: str | Path) -> int:
    """Somme des tailles de tous les fichiers sous `chemin`, récursivement."""
    # TODO : Path(chemin).rglob("*") énumère tout ; garde les p.is_file()
    #        et additionne p.stat().st_size. Une somme sur un générateur :
    #        sum(p.stat().st_size for p in ... if p.is_file())
    raise NotImplementedError("TODO")
