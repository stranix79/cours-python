# outils/texte.py — Labo 06 (solution) : fonctions sur les chaînes.
# Importé par outils/__init__.py et outils/cli.py. Repris du labo 05.


def slugify(texte: str) -> str:
    """'Serveur Web #1 (prod)' → 'serveur-web-1-prod'."""
    caracteres = [c if c.isalnum() else "-" for c in texte.lower()]
    slug = "".join(caracteres)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def parse_kv(texte: str, sep: str = " ") -> dict[str, str | int]:
    """Transforme 'host=web01 port=22' en {'host': 'web01', 'port': 22}."""
    resultat: dict[str, str | int] = {}
    for morceau in texte.split(sep):
        if "=" not in morceau:
            continue
        cle, _, valeur = morceau.partition("=")
        resultat[cle.strip()] = int(valeur) if valeur.isdigit() else valeur
    return resultat
