# outils/dates.py — Labo 20 : fonctions sur les dates. Volontairement sale.
from datetime import date, timedelta, datetime
from typing import List, Optional
import calendar

JOURS_FERIES = ["01-01", "05-01", "07-21", "08-15", "11-01", "11-11", "12-25"]   # Belgique, fixes

def age_en_jours(d, aujourdhui = None):
    if aujourdhui == None:
        aujourdhui = date.today()
    return (aujourdhui - d).days

def est_week_end(d) -> str:
    return d.weekday() >= 5

def est_ferie(d, feries = JOURS_FERIES):
    return d.strftime("%m-%d") in feries

def prochain_jour_ouvre(d, feries = JOURS_FERIES):
    l = d + timedelta(days=1)
    while est_week_end(l) or est_ferie(l, feries) == True:
        l = l + timedelta(days=1)
    return l

def jours_ouvres(debut, fin, exclus = []):
    l = []
    d = debut
    while d <= fin:
        if not est_week_end(d) and not est_ferie(d) and not d in exclus:
            l.append(d)
        d = d + timedelta(days=1)
    return l
