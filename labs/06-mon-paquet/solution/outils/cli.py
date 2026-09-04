# outils/cli.py — Labo 06 (solution) : point d'entrée en ligne de commande.
#
# Lancé de deux façons :
#   python3 -m outils.cli slug "..."   → Python exécute ce module, __name__ == "__main__"
#   outils slug "..."                  → l'exécutable créé par pip ([project.scripts])
#                                        importe ce module et appelle main()
# Dans le second cas, __name__ vaut "outils.cli" et le bloc du bas n'est pas
# exécuté : c'est main() qui est appelé directement. D'où l'importance de
# mettre la logique dans main() et pas sous le if.

import sys

# Imports absolus : on nomme le paquet. Marche partout, y compris avec -m.
from outils.fichiers import taille_dossier, taille_lisible
from outils.reseau import port_ouvert
from outils.texte import slugify

USAGE = """usage : outils <commande> [arguments]

  slug   <texte>         → texte en slug
  taille <chemin>        → taille lisible d'un dossier
  port   <host> <port>   → teste si le port TCP répond
"""


# Chaque commande reçoit la liste des arguments restants (sans le nom de la
# commande) et affiche son résultat. Même signature pour toutes : c'est ce
# qui permet la table de dispatch ci-dessous.
def cmd_slug(args: list[str]) -> None:
    print(slugify(" ".join(args)))


def cmd_taille(args: list[str]) -> None:
    print(taille_lisible(taille_dossier(args[0])))


def cmd_port(args: list[str]) -> None:
    host, port = args[0], int(args[1])
    etat = "ouvert" if port_ouvert(host, port) else "fermé"
    print(f"{host}:{port} {etat}")


# Table de dispatch (chapitre 5) : le nom tapé par l'utilisateur → la fonction.
# Ajouter une commande = une fonction + une ligne ici. Pas de if/elif.
COMMANDES = {
    "slug": cmd_slug,
    "taille": cmd_taille,
    "port": cmd_port,
}


def main() -> None:
    """Lit sys.argv, choisit la commande, l'exécute."""
    # sys.argv = ["outils", "slug", "Hello", "World"] : [0] est le programme.
    args = sys.argv[1:]
    if not args or args[0] not in COMMANDES:
        print(USAGE, file=sys.stderr)     # l'usage va sur stderr, pas stdout
        sys.exit(1)                       # code de retour ≠ 0 = erreur, pour le shell
    try:
        COMMANDES[args[0]](args[1:])
    except (IndexError, ValueError):
        # Pas assez d'arguments, ou un port qui n'est pas un nombre.
        print(USAGE, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
