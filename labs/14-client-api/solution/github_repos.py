# solution/github_repos.py — Labo 14 : client de l'API GitHub, version commentée.
#
# Rôle : lister les dépôts publics d'un utilisateur GitHub (toutes les pages),
#        compter les langages, afficher un tableau.
# Lancé par : python3 github_repos.py stranix79 [--offline] [--base-url URL]
# Importé par : test_github_repos.py (les tests injectent un client httpx factice).
#
# Deux idées de conception à retenir :
#   1. Les fonctions qui parlent au réseau reçoivent le client httpx en
#      paramètre (« injection de dépendance »). Le script principal passe un
#      vrai client ; les tests passent un client avec MockTransport. Aucun
#      test ne touche le réseau.
#   2. Le calcul (compter, formater) est séparé de l'I/O (télécharger,
#      afficher). compter_langages() prend une liste de dicts et rend un
#      dict : testable sans rien d'autre.

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

import httpx

API_GITHUB = "https://api.github.com"
FICHIER_OFFLINE = Path(__file__).parent.parent / "data" / "repos.json"


def creer_client(base_url: str = API_GITHUB, token: str | None = None) -> httpx.Client:
    """Fabrique le client HTTP avec les en-têtes que GitHub recommande.

    Un Client réutilise la connexion TLS entre les pages (une seule poignée de
    main au lieu d'une par requête) et porte les en-têtes communs.
    """
    headers = {
        "Accept": "application/vnd.github+json",   # le format de réponse « officiel »
        "User-Agent": "cours-python-labo14",        # GitHub refuse les requêtes sans UA
    }
    if token:                                       # avec un token : 5000 req/h au lieu de 60
        headers["Authorization"] = f"Bearer {token}"
    # timeout : 10 s. Sans ça, un serveur muet bloque le script pour toujours.
    return httpx.Client(base_url=base_url, headers=headers, timeout=10,
                        follow_redirects=True)


def lister_depots(utilisateur: str, client: httpx.Client, par_page: int = 100) -> list[dict]:
    """Renvoie TOUS les dépôts publics de `utilisateur`, en suivant la pagination.

    GitHub renvoie au plus `per_page` dépôts par réponse et indique la page
    suivante dans l'en-tête Link :
        Link: <https://api.github.com/user/42/repos?page=2>; rel="next", <...>; rel="last"
    httpx le parse pour nous dans resp.links : {"next": {"url": "...", "rel": "next"}, ...}.
    On boucle tant qu'il y a un "next".
    """
    depots: list[dict] = []
    # Première requête : URL relative (le base_url du client complète) + paramètres.
    url: str | None = f"/users/{utilisateur}/repos"
    params: dict | None = {"per_page": par_page, "type": "owner"}
    while url:
        resp = client.get(url, params=params)
        resp.raise_for_status()                     # 404 (utilisateur inconnu), 403 (rate limit)...
        depots.extend(resp.json())
        # L'URL "next" est absolue et contient déjà per_page et page :
        # on ne repasse donc plus params.
        url = resp.links.get("next", {}).get("url")
        params = None
    return depots


def charger_offline(fichier: Path = FICHIER_OFFLINE) -> list[dict]:
    """Mode hors ligne : la même structure, lue depuis un JSON commité dans data/."""
    with fichier.open(encoding="utf-8") as f:
        return json.load(f)


def compter_langages(depots: list[dict]) -> dict[str, int]:
    """Compte les dépôts par langage principal, du plus fréquent au moins fréquent.

    GitHub met `"language": null` quand il n'a rien détecté (dépôt vide, que du
    Markdown...). On regroupe ces cas sous "(aucun)" plutôt que de garder None,
    qui ne se trie pas et s'affiche mal.
    """
    compteur = Counter(depot["language"] or "(aucun)" for depot in depots)
    # most_common() rend une liste de tuples triée ; dict() la retransforme,
    # et un dict garde l'ordre d'insertion (donc l'ordre trié).
    return dict(compteur.most_common())


def formater_tableau(depots: list[dict]) -> str:
    """Construit le tableau texte (une chaîne) : nom, langage, étoiles, dernier push.

    Retourner une chaîne plutôt que print() directement rend la fonction
    testable : le test compare des chaînes, il n'a pas à capturer stdout.
    """
    if not depots:
        return "(aucun dépôt)"
    largeur_nom = max(len(d["name"]) for d in depots)
    lignes = [f"{'dépôt':<{largeur_nom}}  {'langage':<12} {'★':>3}  dernier push"]
    lignes.append("-" * len(lignes[0]))
    # Tri : les plus récemment poussés en premier. pushed_at est ISO 8601, donc
    # l'ordre alphabétique inverse est l'ordre chronologique inverse.
    for d in sorted(depots, key=lambda d: d["pushed_at"] or "", reverse=True):
        langage = d["language"] or "(aucun)"
        lignes.append(f"{d['name']:<{largeur_nom}}  {langage:<12} {d['stargazers_count']:>3}  "
                      f"{(d['pushed_at'] or '')[:10]}")
    return "\n".join(lignes)


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
        # Le token vient de l'environnement, jamais d'un argument ni du code :
        #   export GITHUB_TOKEN=ghp_...
        token = os.environ.get("GITHUB_TOKEN")
        try:
            with creer_client(args.base_url, token) as client:
                depots = lister_depots(args.utilisateur, client)
        except httpx.HTTPStatusError as e:
            # Le serveur a répondu, mais mal. 404 : utilisateur inconnu ;
            # 403 : rate limit épuisé (60/h sans token).
            print(f"erreur HTTP {e.response.status_code} sur {e.request.url}", file=sys.stderr)
            if e.response.status_code == 403:
                reste = e.response.headers.get("X-RateLimit-Remaining")
                print(f"  rate limit restant : {reste} (mets un GITHUB_TOKEN)", file=sys.stderr)
            return 1
        except httpx.TimeoutException:
            print("délai dépassé : GitHub ne répond pas, réessaie (ou --offline)", file=sys.stderr)
            return 2
        except httpx.ConnectError as e:
            print(f"connexion impossible : {e} (pas de réseau ? essaie --offline)", file=sys.stderr)
            return 2

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
    # sys.exit avec le code de retour : 0 = ok, 1 = erreur HTTP, 2 = réseau.
    # Un script shell (ou un cron) peut tester $? .
    sys.exit(main())
