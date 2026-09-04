# outils/__init__.py — Labo 06 (solution) : la façade du paquet.
#
# Rôle : ce fichier est exécuté quand on fait `import outils`. Il transforme
# le dossier en paquet, et il choisit ce que l'utilisateur voit en premier.
# Ici on ré-exporte les fonctions des sous-modules, pour qu'on puisse écrire
#     from outils import slugify
# au lieu de
#     from outils.texte import slugify
# Les deux marchent ; la première cache l'organisation interne, qu'on peut
# changer plus tard sans casser les utilisateurs.

# Import relatif : le point veut dire « dans ce paquet ». Équivalent absolu :
# from outils.texte import slugify. Le relatif est plus court et survit à un
# renommage du paquet.
from .fichiers import taille_dossier, taille_lisible
from .reseau import port_ouvert, retry
from .texte import parse_kv, slugify

# Convention : la version, lisible par  python3 -c "import outils; print(outils.__version__)"
__version__ = "0.1.0"

# __all__ liste ce que  from outils import *  importe. Facultatif, mais c'est
# aussi une documentation de l'API publique, que les linters utilisent.
__all__ = [
    "parse_kv",
    "port_ouvert",
    "retry",
    "slugify",
    "taille_dossier",
    "taille_lisible",
]
