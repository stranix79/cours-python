# solution/dispo.py — Labo 15 : vérificateur de disponibilité, version commentée.
#
# Rôle : lire une liste d'URLs, vérifier chacune en HTTP, et comparer trois
#        stratégies : séquentielle, threads, asyncio (avec sémaphore).
# Lancé par : python3 dispo.py [urls.txt] [--mode seq|threads|async|tous] [--limite N]
# Importé par : test_dispo.py (qui injecte des clients httpx factices).
#
# Chaque stratégie rend la même chose : une liste de Resultat, dans l'ordre
# des URLs. C'est ce qui permet de les comparer et de les tester pareil.

import argparse
import asyncio
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import httpx


@dataclass
class Resultat:
    url: str
    statut: int | None       # code HTTP, ou None si pas de réponse du tout
    duree: float             # secondes
    erreur: str = ""         # vide si tout va bien

    @property
    def ok(self) -> bool:
        return self.statut is not None and self.statut < 400


def lire_urls(fichier: Path) -> list[str]:
    """Une URL par ligne ; lignes vides et commentaires (#) ignorés."""
    urls = []
    for ligne in fichier.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if ligne and not ligne.startswith("#"):
            urls.append(ligne)
    return urls


# ---------------------------------------------------------------------------
# 1. Séquentiel : une requête, on attend, la suivante. La référence.
# ---------------------------------------------------------------------------

def verifier(client: httpx.Client, url: str) -> Resultat:
    """Une vérification bloquante. Toute erreur devient un Resultat, jamais une exception :
    un site en panne ne doit pas faire planter la vérification des 19 autres."""
    debut = time.perf_counter()
    try:
        r = client.get(url)
        return Resultat(url, r.status_code, time.perf_counter() - debut)
    except httpx.HTTPError as e:            # ConnectError, TimeoutException, ...
        # type(e).__name__ donne "ConnectError" : plus lisible que le message
        # complet d'httpx pour un tableau de synthèse.
        return Resultat(url, None, time.perf_counter() - debut, type(e).__name__)


def verifier_sequentiel(urls: list[str], client: httpx.Client) -> list[Resultat]:
    return [verifier(client, url) for url in urls]


# ---------------------------------------------------------------------------
# 2. Threads : la même fonction verifier(), distribuée sur un pool.
#    Pas une ligne de verifier() à changer : c'est l'intérêt des threads pour
#    paralléliser du code bloquant existant.
# ---------------------------------------------------------------------------

def verifier_threads(urls: list[str], client: httpx.Client, limite: int = 10) -> list[Resultat]:
    # httpx.Client est utilisable depuis plusieurs threads. pool.map garde
    # l'ordre des URLs, comme map(). max_workers borne la concurrence, comme
    # le sémaphore de la version async.
    with ThreadPoolExecutor(max_workers=limite) as pool:
        return list(pool.map(lambda url: verifier(client, url), urls))


# ---------------------------------------------------------------------------
# 3. asyncio : un seul thread, une coroutine par URL, un sémaphore pour ne pas
#    tout lancer d'un coup.
# ---------------------------------------------------------------------------

async def verifier_async(client: httpx.AsyncClient, url: str,
                         sem: asyncio.Semaphore) -> Resultat:
    """Même logique que verifier(), avec await là où on attend le réseau."""
    async with sem:                          # attend qu'une place se libère
        debut = time.perf_counter()
        try:
            r = await client.get(url)        # ici, la boucle passe à une autre coroutine
            return Resultat(url, r.status_code, time.perf_counter() - debut)
        except httpx.HTTPError as e:
            return Resultat(url, None, time.perf_counter() - debut, type(e).__name__)


async def verifier_tout_async(urls: list[str], client: httpx.AsyncClient,
                              limite: int = 10) -> list[Resultat]:
    sem = asyncio.Semaphore(limite)
    # TaskGroup (3.11+) : toutes les tâches sont attendues à la sortie du
    # `async with`. Si l'une levait une exception (impossible ici, on les
    # attrape toutes), les autres seraient annulées proprement.
    async with asyncio.TaskGroup() as tg:
        taches = [tg.create_task(verifier_async(client, url, sem)) for url in urls]
    # Les tâches sont finies : .result() ne bloque pas. L'ordre est celui des URLs.
    return [t.result() for t in taches]


def verifier_asyncio(urls: list[str], limite: int = 10, timeout: float = 5) -> list[Resultat]:
    """Pont sync → async : le main() synchrone appelle ceci, qui lance la boucle."""
    async def principal():
        async with httpx.AsyncClient(timeout=timeout) as client:
            return await verifier_tout_async(urls, client, limite)
    return asyncio.run(principal())


# ---------------------------------------------------------------------------
# Affichage et point d'entrée
# ---------------------------------------------------------------------------

def formater(resultats: list[Resultat]) -> str:
    lignes = []
    for r in resultats:
        etat = "OK " if r.ok else "KO "
        statut = str(r.statut) if r.statut is not None else "---"
        lignes.append(f"{etat} {statut} {r.duree:6.2f} s  {r.url}  {r.erreur}".rstrip())
    ok = sum(1 for r in resultats if r.ok)
    lignes.append(f"{ok}/{len(resultats)} disponibles")
    return "\n".join(lignes)


def chronometrer(nom: str, fonction) -> list[Resultat]:
    debut = time.perf_counter()
    resultats = fonction()
    print(f"--- {nom:<10} : {time.perf_counter() - debut:5.2f} s")
    return resultats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Vérifie la disponibilité d'une liste d'URLs.")
    parser.add_argument("fichier", nargs="?", default=Path(__file__).parent.parent / "urls.txt",
                        type=Path)
    parser.add_argument("--mode", choices=["seq", "threads", "async", "tous"], default="tous")
    parser.add_argument("--limite", type=int, default=10, help="requêtes simultanées max")
    parser.add_argument("--timeout", type=float, default=5)
    parser.add_argument("--detail", action="store_true", help="afficher chaque URL")
    args = parser.parse_args(argv)

    urls = lire_urls(args.fichier)
    print(f"{len(urls)} URLs, limite {args.limite}, timeout {args.timeout} s")

    resultats: list[Resultat] = []
    with httpx.Client(timeout=args.timeout) as client:
        if args.mode in ("seq", "tous"):
            resultats = chronometrer("séquentiel", lambda: verifier_sequentiel(urls, client))
        if args.mode in ("threads", "tous"):
            resultats = chronometrer("threads", lambda: verifier_threads(urls, client, args.limite))
    if args.mode in ("async", "tous"):
        resultats = chronometrer("asyncio", lambda: verifier_asyncio(urls, args.limite, args.timeout))

    if args.detail:
        print(formater(resultats))
    else:
        print(formater(resultats).splitlines()[-1])
    # Code de retour : 0 si tout est disponible, 1 sinon. Utile dans un cron
    # ou un healthcheck Docker.
    return 0 if all(r.ok for r in resultats) else 1


if __name__ == "__main__":
    sys.exit(main())
