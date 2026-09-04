# hello.py — Labo 01 : premier script.
# Affiche un salut, la version de Python, l'OS, et l'heure Unix.

import sys
import platform
import time

nom = "stranix"          # TODO : mets ton nom

print(f"Bonjour, {nom} !")

# TODO : affiche « Python X.Y.Z sur <système> »
#   - la version : sys.version_info donne un tuple (3, 13, 5, ...) ;
#     essaie aussi platform.python_version() qui donne directement "3.13.5"
#   - le système : platform.system() → "Darwin", "Linux" ou "Windows"

# TODO : affiche le nombre de secondes depuis le 1er janvier 1970, arrondi
#   - time.time() donne un float ; int(...) ou round(...) pour l'arrondir
