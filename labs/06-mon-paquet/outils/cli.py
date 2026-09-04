# outils/cli.py — Labo 06 : point d'entrée en ligne de commande.
# Lancé par : python3 -m outils.cli ..., ou par la commande `outils` une fois
# le paquet installé ([project.scripts] dans pyproject.toml → main()).

import sys

# TODO : importe les fonctions dont tu as besoin depuis les sous-modules.
#        Import absolu : from outils.texte import slugify
#        ou relatif   : from .texte import slugify   (le . = « ce paquet »)

USAGE = """usage : outils <commande> [arguments]

  slug   <texte>         → texte en slug
  taille <chemin>        → taille lisible d'un dossier
  port   <host> <port>   → teste si le port TCP répond
"""


def cmd_slug(args: list[str]) -> None:
    # TODO : print(slugify(" ".join(args)))
    raise NotImplementedError("TODO")


def cmd_taille(args: list[str]) -> None:
    # TODO : print(taille_lisible(taille_dossier(args[0])))
    raise NotImplementedError("TODO")


def cmd_port(args: list[str]) -> None:
    # TODO : host, port = args[0], int(args[1]) ; print("ouvert" ou "fermé")
    raise NotImplementedError("TODO")


# TODO : table de dispatch : nom de commande → fonction (chapitre 5)
COMMANDES = {}


def main() -> None:
    """Lit sys.argv, choisit la commande, l'exécute."""
    # sys.argv[0] est le nom du script ; les vrais arguments commencent à 1.
    # TODO : si pas d'argument ou commande inconnue → print(USAGE) ; sys.exit(1)
    #        sinon COMMANDES[commande](sys.argv[2:])
    raise NotImplementedError("TODO")


if __name__ == "__main__":
    main()
