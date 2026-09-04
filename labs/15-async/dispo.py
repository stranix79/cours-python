# dispo.py — Labo 15 : vérificateur de disponibilité.
# Lit une liste d'URLs et vérifie chacune en HTTP, de trois façons :
# séquentielle, threads, asyncio (avec sémaphore). Compare les temps.
#
# Chaque stratégie rend une liste de Resultat, DANS L'ORDRE DES URLS.
# Toute erreur réseau devient un Resultat avec statut None : jamais une
# exception (un site en panne ne doit pas faire planter les autres).

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
    # TODO : fichier.read_text(encoding="utf-8").splitlines(), strip(), filtrer
    raise NotImplementedError("TODO lire_urls")


# --- 1. Séquentiel ----------------------------------------------------------

def verifier(client: httpx.Client, url: str) -> Resultat:
    """Une vérification bloquante : client.get(url), mesure le temps (time.perf_counter()).
    Attrape httpx.HTTPError et renvoie Resultat(url, None, duree, type(e).__name__)."""
    raise NotImplementedError("TODO verifier")


def verifier_sequentiel(urls: list[str], client: httpx.Client) -> list[Resultat]:
    # TODO : une compréhension de liste sur verifier()
    raise NotImplementedError("TODO verifier_sequentiel")


# --- 2. Threads ---------------------------------------------------------------

def verifier_threads(urls: list[str], client: httpx.Client, limite: int = 10) -> list[Resultat]:
    # TODO : ThreadPoolExecutor(max_workers=limite) et pool.map(...) sur verifier().
    #        Le même client httpx peut être partagé entre threads.
    raise NotImplementedError("TODO verifier_threads")


# --- 3. asyncio ---------------------------------------------------------------

async def verifier_async(client: httpx.AsyncClient, url: str,
                         sem: asyncio.Semaphore) -> Resultat:
    """Même logique que verifier(), avec `await client.get(url)` sous `async with sem:`."""
    raise NotImplementedError("TODO verifier_async")


async def verifier_tout_async(urls: list[str], client: httpx.AsyncClient,
                              limite: int = 10) -> list[Resultat]:
    # TODO : sem = asyncio.Semaphore(limite) ; un asyncio.TaskGroup() dans lequel
    #        tu crées une tâche par URL ; à la sortie, [t.result() for t in taches].
    #        (asyncio.gather(*coroutines) marche aussi.)
    raise NotImplementedError("TODO verifier_tout_async")


def verifier_asyncio(urls: list[str], limite: int = 10, timeout: float = 5) -> list[Resultat]:
    """Pont sync → async : ouvre un httpx.AsyncClient(timeout=timeout) et lance la boucle."""
    # TODO : une coroutine interne `principal()` qui fait `async with httpx.AsyncClient(...)`
    #        puis `return await verifier_tout_async(...)` ; renvoie asyncio.run(principal())
    raise NotImplementedError("TODO verifier_asyncio")


# --- Affichage et point d'entrée ------------------------------------------------

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
    parser.add_argument("fichier", nargs="?", default=Path(__file__).parent / "urls.txt", type=Path)
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
    return 0 if all(r.ok for r in resultats) else 1


if __name__ == "__main__":
    sys.exit(main())
