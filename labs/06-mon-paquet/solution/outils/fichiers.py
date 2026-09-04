# outils/fichiers.py — Labo 06 (solution) : tailles de fichiers et de dossiers.
# Importé par outils/__init__.py et outils/cli.py.

from pathlib import Path

UNITES = ("o", "Ko", "Mo", "Go", "To")


def taille_lisible(octets: int, decimales: int = 1) -> str:
    """1536 → '1.5 Ko'. Base 1024, comme `du -h`."""
    if octets < 1024:
        return f"{octets} o"
    valeur = float(octets)
    for unite in UNITES:
        if valeur < 1024:
            break
        valeur /= 1024
    else:
        unite = UNITES[-1]
        valeur *= 1024
    return f"{valeur:.{decimales}f} {unite}"


def taille_dossier(chemin: str | Path) -> int:
    """Somme des tailles de tous les fichiers sous `chemin`, récursivement.

    Équivalent de `du -sb`. Les liens symboliques ne sont pas suivis
    (is_file() est vrai pour un lien vers un fichier, mais rglob ne descend
    pas dans un lien vers un dossier).
    """
    # Path(chemin) accepte une str ou déjà un Path : idempotent.
    # rglob("*") = glob récursif, un générateur (chapitre 11) : il ne construit
    # pas la liste complète en mémoire, il produit les chemins un par un.
    # sum(...) consomme ce générateur ; l'expression entre parenthèses est une
    # expression génératrice, une compréhension sans crochets.
    return sum(p.stat().st_size for p in Path(chemin).rglob("*") if p.is_file())
