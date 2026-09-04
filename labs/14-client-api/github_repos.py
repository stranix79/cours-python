# github_repos.py — Labo 14 : client de l'API GitHub.
# Liste les dépôts publics d'un utilisateur (toutes les pages), compte les
# langages, affiche un tableau. Mode --offline : lit data/repos.json.
#
# Les fonctions reçoivent le client httpx en paramètre : les tests en passent
# un factice (httpx.MockTransport), le main() en passe un vrai.

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

import httpx

API_GITHUB = "https://api.github.com"
FICHIER_OFFLINE = Path(__file__).parent / "data" / "repos.json"


def creer_client(base_url: str = API_GITHUB, token: str | None = None) -> httpx.Client:
    """Fabrique le client HTTP avec les bons en-têtes et un timeout."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "cours-python-labo14",
    }
    # TODO : si token n'est pas None, ajoute l'en-tête Authorization: Bearer <token>
    # TODO : renvoie un httpx.Client(base_url=..., headers=..., timeout=10, follow_redirects=True)
    raise NotImplementedError("TODO creer_client")


def lister_depots(utilisateur: str, client: httpx.Client, par_page: int = 100) -> list[dict]:
    """Renvoie TOUS les dépôts publics de `utilisateur`, en suivant la pagination."""
    depots: list[dict] = []
    # TODO : première requête : client.get(f"/users/{utilisateur}/repos",
    #        params={"per_page": par_page, "type": "owner"})
    # TODO : resp.raise_for_status(), puis depots.extend(resp.json())
    # TODO : page suivante : resp.links.get("next", {}).get("url") → None s'il n'y en a plus.
    #        Boucle tant qu'il y a une URL. Attention : l'URL "next" contient déjà
    #        les paramètres, ne repasse pas params.
    raise NotImplementedError("TODO lister_depots")


def charger_offline(fichier: Path = FICHIER_OFFLINE) -> list[dict]:
    """Mode hors ligne : la même structure, lue depuis data/repos.json."""
    # TODO : ouvre le fichier (encoding="utf-8") et renvoie json.load(f)
    raise NotImplementedError("TODO charger_offline")


def compter_langages(depots: list[dict]) -> dict[str, int]:
    """Compte les dépôts par langage principal, du plus fréquent au moins fréquent.

    `"language": null` (dépôt sans code détecté) doit être compté sous "(aucun)".
    """
    # TODO : un Counter sur depot["language"] or "(aucun)", puis dict(compteur.most_common())
    raise NotImplementedError("TODO compter_langages")


def formater_tableau(depots: list[dict]) -> str:
    """Construit le tableau texte : nom, langage, étoiles, date du dernier push (AAAA-MM-JJ).

    Trié par pushed_at décroissant. Renvoie "(aucun dépôt)" si la liste est vide.
    """
    # TODO : une ligne d'en-tête, une ligne de tirets, une ligne par dépôt.
    #        Largeur de la colonne nom = le nom le plus long (max(len(...))).
    #        f"{valeur:<{largeur}}" aligne à gauche, f"{n:>3}" à droite.
    raise NotImplementedError("TODO formater_tableau")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dépôts publics d'un utilisateur GitHub.")
    parser.add_argument("utilisateur", nargs="?", default="stranix79")
    parser.add_argument("--offline", action="store_true",
                        help="lire data/repos.json au lieu d'appeler GitHub")
    parser.add_argument("--base-url", default=API_GITHUB,
                        help="racine de l'API (pour pointer sur un serveur local)")
    parser.add_argument("--json", action="store_true", help="sortie JSON brute")
    args = parser.parse_args(argv)

    if args.offline:
        depots = charger_offline()
    else:
        token = os.environ.get("GITHUB_TOKEN")      # jamais en argument, jamais dans le code
        # TODO : with creer_client(args.base_url, token) as client: depots = lister_depots(...)
        # TODO : attrape séparément httpx.HTTPStatusError (→ return 1, affiche le code),
        #        httpx.TimeoutException et httpx.ConnectError (→ return 2, suggère --offline)
        raise NotImplementedError("TODO main : appel réseau")

    if args.json:
        print(json.dumps(depots, indent=2, ensure_ascii=False))
        return 0

    print(formater_tableau(depots))
    print()
    print(f"{len(depots)} dépôts, par langage :")
    for langage, nombre in compter_langages(depots).items():
        print(f"  {langage:<12} {nombre:>3}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
