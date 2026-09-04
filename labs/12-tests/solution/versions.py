# solution/versions.py — Labo 12 : parser, comparer et faire évoluer des versions semver.
#
# Rôle : le module testé. Une Version est un triplet (majeur, mineur, correctif),
#        « 1.2.3 » selon https://semver.org (sans les suffixes -beta et +build).
# Importé par : test_versions.py (et par n'importe quel script d'outillage
#        qui doit décider si « 2.3.1 » satisfait « ^2.1.0 »).

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Version:
    """Un triplet semver. frozen : immuable (donc hachable, utilisable en clé de dict).
    order=True : génère <, <=, >, >= qui comparent champ par champ, dans l'ordre
    de déclaration : majeur, puis mineur, puis correctif. Exactement l'ordre semver."""

    majeur: int
    mineur: int
    correctif: int

    def __str__(self) -> str:
        return f"{self.majeur}.{self.mineur}.{self.correctif}"


def parse(texte: str) -> Version:
    """« 1.2.3 » ou « v1.2.3 » → Version(1, 2, 3). ValueError si le format est mauvais."""
    texte = texte.strip()
    if texte.startswith("v"):           # tolérance : les tags git sont souvent « v1.2.3 »
        texte = texte[1:]
    morceaux = texte.split(".")
    if len(morceaux) != 3:
        raise ValueError(f"version invalide : {texte!r} (attendu MAJEUR.MINEUR.CORRECTIF)")
    try:
        majeur, mineur, correctif = (int(m) for m in morceaux)
    except ValueError:                  # int("x") lève ValueError : on la reformule
        raise ValueError(f"version invalide : {texte!r} (chaque partie doit être un entier)") from None
    if min(majeur, mineur, correctif) < 0:
        raise ValueError(f"version invalide : {texte!r} (pas de nombre négatif)")
    return Version(majeur, mineur, correctif)


def bump(version: Version, partie: str) -> Version:
    """Incrémente une partie et remet à zéro celles de droite : semver oblige.
    bump(1.2.3, "minor") → 1.3.0 ; bump(1.2.3, "major") → 2.0.0."""
    match partie:                       # match (chapitre 3) : plus lisible qu'un if/elif ici
        case "major":
            return Version(version.majeur + 1, 0, 0)
        case "minor":
            return Version(version.majeur, version.mineur + 1, 0)
        case "patch":
            return Version(version.majeur, version.mineur, version.correctif + 1)
        case _:
            raise ValueError(f"partie inconnue : {partie!r} (major, minor ou patch)")


def compatible(version: Version, contrainte: str) -> bool:
    """Teste une contrainte à la npm / cargo :
      « ^1.2.0 » : même majeur, et >= 1.2.0      (compatible : l'API ne casse pas)
      « ~1.2.0 » : même majeur.mineur, et >= 1.2.0 (correctifs seulement)
      « 1.2.0 »  : exactement cette version
      « >=1.2.0 », « >1.2.0 », « <2.0.0 », « <=2.0.0 » : comparaison simple
      « >=1.2.0,<2.0.0 » : toutes les contraintes séparées par une virgule (ET logique)."""
    if "," in contrainte:
        # all() sur une expression génératrice : s'arrête à la première fausse
        return all(compatible(version, c) for c in contrainte.split(","))

    contrainte = contrainte.strip()
    # On teste les opérateurs à deux caractères AVANT ceux à un caractère,
    # sinon « >=1.2.0 » serait pris pour « > » suivi de « =1.2.0 ».
    for prefixe in ("^", "~", ">=", "<=", ">", "<"):
        if contrainte.startswith(prefixe):
            borne = parse(contrainte[len(prefixe):])
            break
    else:                               # for ... else : exécuté si aucun break (chapitre 3)
        prefixe = ""
        borne = parse(contrainte)

    match prefixe:
        case "^":
            return version.majeur == borne.majeur and version >= borne
        case "~":
            return (version.majeur, version.mineur) == (borne.majeur, borne.mineur) and version >= borne
        case ">=":
            return version >= borne
        case "<=":
            return version <= borne
        case ">":
            return version > borne
        case "<":
            return version < borne
        case _:
            return version == borne
