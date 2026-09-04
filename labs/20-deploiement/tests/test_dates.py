# tests/test_dates.py — Labo 20 : tests du module dates (ils passent avant ET après le nettoyage).
from datetime import date

from outils import dates


def test_age_en_jours():
    assert dates.age_en_jours(date(2026, 1, 1), aujourdhui=date(2026, 1, 11)) == 10


def test_week_end():
    assert dates.est_week_end(date(2026, 9, 5))        # samedi
    assert not dates.est_week_end(date(2026, 9, 7))    # lundi


def test_ferie():
    assert dates.est_ferie(date(2026, 7, 21))          # fête nationale belge
    assert not dates.est_ferie(date(2026, 7, 22))


def test_prochain_jour_ouvre_saute_le_week_end_et_les_feries():
    # vendredi 31 juillet 2026 → samedi, dimanche, puis lundi 3 août
    assert dates.prochain_jour_ouvre(date(2026, 7, 31)) == date(2026, 8, 3)
    # jeudi 24 décembre → 25 férié, 26 samedi, 27 dimanche → lundi 28
    assert dates.prochain_jour_ouvre(date(2026, 12, 24)) == date(2026, 12, 28)


def test_jours_ouvres():
    # semaine du 7 au 13 septembre 2026 : lundi à vendredi = 5 jours
    assert len(dates.jours_ouvres(date(2026, 9, 7), date(2026, 9, 13))) == 5
