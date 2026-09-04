# versions.py — Labo 12 : parser, comparer et faire évoluer des versions semver.
# Importé par : test_versions.py
#
# Une Version est un triplet (majeur, mineur, correctif) : « 1.2.3 » (https://semver.org).

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Version:
    """frozen : immuable et hachable. order=True : <, <=, >, >= champ par champ,
    dans l'ordre de déclaration, donc majeur puis mineur puis correctif."""

    majeur: int
    mineur: int
    correctif: int

    def __str__(self) -> str:
        return f"{self.majeur}.{self.mineur}.{self.correctif}"


def parse(texte: str) -> Version:
    """« 1.2.3 » ou « v1.2.3 » (espaces tolérés) → Version(1, 2, 3).
    ValueError avec un message utile si : pas trois parties, partie non entière, négatif."""
    # TODO : strip(), enlever un « v » initial, split("."), vérifier len == 3,
    #        int() sur chaque partie (attrape ValueError et relève avec un meilleur message),
    #        refuser les négatifs.
    raise NotImplementedError("TODO")


def bump(version: Version, partie: str) -> Version:
    """Incrémente une partie (« major », « minor », « patch ») et remet à zéro celles
    de droite : bump(1.2.3, "minor") → 1.3.0. ValueError si partie inconnue."""
    # TODO : match partie: case "major": ... ; Version est immuable → construis-en une nouvelle
    raise NotImplementedError("TODO")


def compatible(version: Version, contrainte: str) -> bool:
    """Contraintes à la npm / cargo :
      « ^1.2.0 » : même majeur et >= 1.2.0
      « ~1.2.0 » : même majeur.mineur et >= 1.2.0
      « 1.2.0 »  : égalité exacte
      « >=1.2.0 », « >1.2.0 », « <2.0.0 », « <=2.0.0 »
      « >=1.2.0,<2.0.0 » : plusieurs contraintes, toutes doivent être vraies."""
    # TODO : si « , » dans contrainte → all(compatible(version, c) for c in ...)
    #        sinon détecter le préfixe (teste ">=" et "<=" AVANT ">" et "<"),
    #        parse() le reste, comparer. Les comparaisons de Version marchent déjà.
    raise NotImplementedError("TODO")
