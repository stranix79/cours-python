# solution/test_versions.py — Labo 12 : les tests de versions.py, version complète.
#
# Rôle : spécifier le comportement de versions.py, exemple par exemple.
# Lancé par : SOLUTION=1 pytest solution/   (depuis labs/12-tests/)
#
# Chaque fonction test_* est découverte par pytest. Un test = préparer, appeler,
# vérifier avec assert. Un test qui ne lève rien passe ; un assert faux ou une
# exception le fait échouer.

import pytest

from versions import Version, bump, compatible, parse


# --- parse -----------------------------------------------------------------

def test_parse_simple():
    assert parse("1.2.3") == Version(1, 2, 3)


def test_parse_prefixe_v_et_espaces():
    # Les tags git sont souvent « v1.2.3 » ; parse doit être tolérant là-dessus.
    assert parse(" v1.2.3\n") == Version(1, 2, 3)


# Un seul test, six cas : pytest crée un test par tuple, avec un nom lisible
# (test_parse_invalide[1.2] …). Bien plus court que six fonctions.
@pytest.mark.parametrize("texte", ["1.2", "1.2.3.4", "a.b.c", "1.-2.3", "", "1..3"])
def test_parse_invalide(texte):
    with pytest.raises(ValueError):     # le test passe SEULEMENT si ValueError est levée
        parse(texte)


def test_parse_message_d_erreur_utile():
    # match= est une regex cherchée dans le message : on vérifie que l'erreur
    # explique ce qui ne va pas, pas juste qu'elle existe.
    with pytest.raises(ValueError, match="MAJEUR.MINEUR.CORRECTIF"):
        parse("1.2")


# --- comparaison -------------------------------------------------------------

@pytest.mark.parametrize("petite, grande", [
    ("1.0.0", "2.0.0"),
    ("1.2.0", "1.10.0"),    # 10 > 2 : comparaison numérique, pas alphabétique
    ("1.2.3", "1.2.10"),
    ("0.9.9", "1.0.0"),
])
def test_ordre(petite, grande):
    assert parse(petite) < parse(grande)
    assert parse(grande) > parse(petite)
    assert parse(petite) != parse(grande)


def test_egalite_et_hash():
    # frozen=True rend Version hachable : elle peut servir de clé de dict ou d'élément de set.
    assert parse("1.2.3") == parse("1.2.3")
    assert len({parse("1.2.3"), parse("1.2.3"), parse("1.2.4")}) == 2


def test_str():
    assert str(Version(1, 2, 3)) == "1.2.3"


# --- bump --------------------------------------------------------------------

@pytest.mark.parametrize("partie, attendu", [
    ("major", "2.0.0"),
    ("minor", "1.3.0"),
    ("patch", "1.2.4"),
])
def test_bump(partie, attendu):
    assert bump(parse("1.2.3"), partie) == parse(attendu)


def test_bump_ne_modifie_pas_l_original():
    # Version est immuable : bump rend un NOUVEL objet, l'ancien reste intact.
    # C'est le genre de test qu'on écrit après s'être fait avoir une fois.
    v = parse("1.2.3")
    bump(v, "major")
    assert v == parse("1.2.3")


def test_bump_partie_inconnue():
    with pytest.raises(ValueError, match="major, minor ou patch"):
        bump(parse("1.2.3"), "mega")


# --- compatible --------------------------------------------------------------

@pytest.mark.parametrize("version, contrainte, attendu", [
    ("1.2.3", "^1.2.0", True),
    ("1.9.0", "^1.2.0", True),
    ("2.0.0", "^1.2.0", False),      # changement de majeur : API cassée
    ("1.1.9", "^1.2.0", False),      # trop vieux
    ("1.2.9", "~1.2.0", True),
    ("1.3.0", "~1.2.0", False),      # ~ n'accepte que les correctifs
    ("1.2.3", "1.2.3", True),
    ("1.2.4", "1.2.3", False),
    ("1.5.0", ">=1.2.0", True),
    ("1.5.0", ">1.5.0", False),
    ("1.5.0", "<2.0.0", True),
    ("2.0.0", "<=2.0.0", True),
    ("1.5.0", ">=1.2.0,<2.0.0", True),
    ("2.1.0", ">=1.2.0,<2.0.0", False),
])
def test_compatible(version, contrainte, attendu):
    assert compatible(parse(version), contrainte) is attendu


def test_compatible_contrainte_invalide():
    with pytest.raises(ValueError):
        compatible(parse("1.0.0"), "^abc")
