# test_versions.py — Labo 12 : les tests de versions.py. C'est TOI qui les écris.
# Lancé par : pytest   (dans labs/12-tests/)
#
# Deux tests sont donnés en exemple. Les autres sont à écrire : enlève le
# @pytest.mark.skip et remplace le corps. Écris le test AVANT le code (TDD) :
# il doit d'abord échouer (rouge), puis passer quand versions.py est complet (vert).

import pytest

from versions import Version, bump, compatible, parse


# --- parse : deux exemples donnés --------------------------------------------

def test_parse_simple():
    assert parse("1.2.3") == Version(1, 2, 3)


@pytest.mark.parametrize("texte", ["1.2", "1.2.3.4", "a.b.c"])
def test_parse_invalide(texte):
    with pytest.raises(ValueError):
        parse(texte)


# --- à toi ---------------------------------------------------------------------

@pytest.mark.skip(reason="TODO : à écrire")
def test_parse_prefixe_v_et_espaces():
    # « v1.2.3 » et les espaces autour doivent être acceptés.
    ...


@pytest.mark.skip(reason="TODO : à écrire (parametrize avec 3 ou 4 couples)")
def test_ordre():
    # 1.2.0 < 1.10.0 (numérique, pas alphabétique !), 0.9.9 < 1.0.0, ...
    ...


@pytest.mark.skip(reason="TODO : à écrire")
def test_egalite_et_hash():
    # deux parse("1.2.3") sont égaux, et un set n'en garde qu'un
    ...


@pytest.mark.skip(reason="TODO : à écrire (parametrize major/minor/patch)")
def test_bump():
    ...


@pytest.mark.skip(reason="TODO : à écrire")
def test_bump_ne_modifie_pas_l_original():
    ...


@pytest.mark.skip(reason="TODO : à écrire (pytest.raises avec match=)")
def test_bump_partie_inconnue():
    ...


@pytest.mark.skip(reason="TODO : à écrire (parametrize : au moins 10 cas, ^ ~ = >= < et virgule)")
def test_compatible():
    ...
