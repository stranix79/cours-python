# solution/hello.py — Labo 01 : premier script, version commentée.
#
# Rôle : afficher un salut, la version de Python, l'OS et l'heure Unix.
# Lancé par : python3 solution/hello.py (aucun autre fichier ne l'importe).
#
# Un script Python est exécuté de haut en bas, comme un script shell.
# Pas de main() obligatoire : la première ligne exécutable est la première
# instruction du fichier.

import sys                  # accès à l'interpréteur : version, arguments, PATH des modules
import platform             # infos sur la machine : OS, architecture, version de Python
import time                 # horloge : time.time() = secondes depuis le 1er janvier 1970

# Une variable n'a pas de type déclaré : c'est la valeur "stranix" qui est
# une chaîne (str). En C on aurait écrit : const char *nom = "stranix";
nom = "stranix"

# f-string : le f devant les guillemets active l'évaluation des {} .
# Équivalent C : printf("Bonjour, %s !\n", nom);  (print ajoute le \n tout seul)
print(f"Bonjour, {nom} !")

# platform.python_version() renvoie directement "3.13.5" (une chaîne).
# sys.version_info est un tuple (3, 13, 5, 'final', 0) : pratique pour comparer,
# par exemple  if sys.version_info >= (3, 11):
version = platform.python_version()
systeme = platform.system()         # "Darwin" sur macOS, "Linux", "Windows"

# print accepte plusieurs arguments et les sépare par un espace.
print("Python", version, "sur", systeme)

# time.time() renvoie un float (1725456789.123456). int() tronque, round()
# arrondit au plus proche. Ici les deux se valent : on veut juste un entier.
maintenant = int(time.time())
print(f"Secondes depuis le 1er janvier 1970 : {maintenant}")

# Pour le point 4 du labo : décommente la ligne suivante et lis le traceback.
# La dernière ligne dit QUOI (AttributeError + suggestion), celle du dessus dit OÙ.
# print(time.tim())
