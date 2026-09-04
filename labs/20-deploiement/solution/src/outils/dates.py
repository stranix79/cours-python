# src/outils/dates.py — Labo 20 (solution) : fonctions sur les dates, nettoyées.
#
# Rôle : jours ouvrés, week-ends, fériés belges à date fixe.
# Utilisé par : outils.cli, tests/test_dates.py.
"""Calculs de jours ouvrés (Belgique, fériés à date fixe seulement)."""

from collections.abc import Iterable
from datetime import date, timedelta

# Une constante : UPPER_SNAKE, et un tuple plutôt qu'une liste, parce qu'elle
# ne doit pas changer. Fériés belges à date fixe (Pâques, Ascension, Pentecôte
# bougent : hors périmètre de ce paquet).
JOURS_FERIES: tuple[str, ...] = (
    "01-01",
    "05-01",
    "07-21",
    "08-15",
    "11-01",
    "11-11",
    "12-25",
)


def age_en_jours(d: date, aujourdhui: date | None = None) -> int:
    """Nombre de jours entre `d` et `aujourdhui` (par défaut : la date du jour)."""
    # `is None`, jamais `== None` : on teste l'identité avec LE singleton None,
    # pas une égalité que n'importe quel objet pourrait redéfinir (E711).
    if aujourdhui is None:
        aujourdhui = date.today()
    return (aujourdhui - d).days


def est_week_end(d: date) -> bool:
    # L'annotation d'origine disait -> str : mypy a signalé qu'on renvoyait
    # autre chose. Une annotation fausse est pire que pas d'annotation.
    return d.weekday() >= 5


def est_ferie(d: date, feries: Iterable[str] = JOURS_FERIES) -> bool:
    # Iterable[str] : on accepte tuple, liste, set… tout ce qu'on peut parcourir.
    return d.strftime("%m-%d") in feries


def prochain_jour_ouvre(d: date, feries: Iterable[str] = JOURS_FERIES) -> date:
    """Premier jour après `d` qui n'est ni un week-end ni un férié."""
    # `feries` est un Iterable : s'il ne se parcourt qu'une fois (un générateur),
    # la boucle le viderait au premier tour. On le fige en set, et le test `in`
    # devient O(1) au passage.
    feries = set(feries)
    suivant = d + timedelta(days=1)
    # `== True` supprimé (E712) : un booléen se teste directement.
    while est_week_end(suivant) or est_ferie(suivant, feries):
        suivant += timedelta(days=1)
    return suivant


def jours_ouvres(debut: date, fin: date, exclus: Iterable[date] = ()) -> list[date]:
    """Liste des jours ouvrés de `debut` à `fin` inclus, moins les dates `exclus`."""
    # Le défaut `exclus=[]` d'origine (B006) est LE piège classique : la liste
    # est créée une fois à la définition et partagée entre tous les appels.
    # Un tuple vide est immuable, donc sans danger comme défaut.
    exclus = set(exclus)
    resultat: list[date] = []
    d = debut
    while d <= fin:
        if not est_week_end(d) and not est_ferie(d) and d not in exclus:
            resultat.append(d)
        d += timedelta(days=1)
    return resultat
