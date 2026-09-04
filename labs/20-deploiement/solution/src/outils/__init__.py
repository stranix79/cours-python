# src/outils/__init__.py — Labo 20 (solution) : le paquet `outils`.
#
# Rôle : marquer le dossier comme paquet et exposer __version__.
# Importé par : tout `import outils`, et par pip au moment de l'installation.
"""Petits utilitaires dates et réseau."""

from importlib.metadata import version

# Lu dans les métadonnées du paquet installé (pip install -e . suffit) : le
# numéro n'existe qu'à un endroit, dans pyproject.toml. Avant, on le copiait
# ici à la main et les deux finissaient toujours par diverger.
__version__ = version("outils")
