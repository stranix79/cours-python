# pipeline.py — Labo 11 : analyse d'un access.log nginx avec des générateurs.
# Lancé par : python3 pipeline.py [chemin_du_log]
#
# Architecture = un tube Unix : lire_lignes() | parser() | filtrer_code() | Counter
# Chaque étage est un générateur. Rien n'est stocké tant qu'on n'agrège pas.

import functools
import re
import sys
import time
from collections import Counter
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path


def chrono(fonction):
    """Décorateur : affiche la durée de l'appel sur stderr."""
    # TODO : enveloppe(*args, **kwargs) qui mesure avec time.perf_counter(),
    #        appelle fonction, affiche « [chrono] nom : X.X ms » sur stderr
    #        (print(..., file=sys.stderr)) et RENVOIE le résultat.
    #        N'oublie pas @functools.wraps(fonction) sur l'enveloppe.
    return fonction


@contextmanager
def fichier_log(chemin: Path):
    """Ouvre le fichier, affiche [ouverture]/[fermeture] sur stderr, ferme quoi qu'il arrive."""
    # TODO : print [ouverture], open(), yield f dans un try/finally qui close() et print [fermeture]
    f = open(chemin, encoding="utf-8")
    yield f
    f.close()


def lire_lignes(chemin: Path) -> Iterator[str]:
    """Étage 1 : rend les lignes du fichier une à une, sans le \\n."""
    # TODO : with fichier_log(chemin) as f, boucle for, yield ligne.rstrip("\n")
    raise NotImplementedError("TODO")


# Format nginx "combined" :
# 203.0.113.42 - - [03/Sep/2026:08:00:10 +0200] "GET /.env HTTP/1.1" 404 15908 "-" "curl/8.7.1"
FORMAT_COMBINED = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<date>[^\]]+)\] '
    r'"(?P<methode>[A-Z]+) (?P<chemin>\S+) [^"]*" '
    r'(?P<code>\d{3}) (?P<taille>\d+) "(?P<referer>[^"]*)" "(?P<agent>[^"]*)"'
)


def parser(lignes: Iterable[str]) -> Iterator[dict]:
    """Étage 2 : transforme chaque ligne en dict (ip, date, methode, chemin, code, taille, ...)."""
    # TODO : pour chaque ligne, m = FORMAT_COMBINED.match(ligne) ; si None, ignorer ;
    #        sinon d = m.groupdict(), convertir code et taille en int, yield d
    raise NotImplementedError("TODO")


def filtrer_code(entrees: Iterable[dict], minimum: int, maximum: int = 599) -> Iterator[dict]:
    """Étage 3 : ne garde que les entrées dont minimum <= code <= maximum."""
    # TODO
    raise NotImplementedError("TODO")


def filtrer_chemin(entrees: Iterable[dict], prefixe: str) -> Iterator[dict]:
    """Étage 3 bis : ne garde que les chemins qui commencent par prefixe."""
    # TODO : str.startswith
    raise NotImplementedError("TODO")


@chrono
def top_ips(entrees: Iterable[dict], n: int = 5) -> list[tuple[str, int]]:
    """Les n IP les plus fréquentes : [(ip, nombre), ...]."""
    # TODO : Counter(expression génératrice).most_common(n)
    raise NotImplementedError("TODO")


@chrono
def repartition_codes(entrees: Iterable[dict]) -> Counter:
    """Counter {code: nombre}."""
    # TODO
    raise NotImplementedError("TODO")


@chrono
def octets_par_chemin(entrees: Iterable[dict]) -> Counter:
    """Counter {chemin: total des octets servis}."""
    # TODO : total[e["chemin"]] += e["taille"]
    raise NotImplementedError("TODO")


def suivre(chemin: Path, intervalle: float = 0.5) -> Iterator[str]:
    """Bonus : tail -f. Générateur infini des nouvelles lignes ajoutées au fichier."""
    # TODO : open, f.seek(0, 2) pour aller à la fin, boucle infinie :
    #        ligne = f.readline() ; si ligne → yield, sinon time.sleep(intervalle)
    raise NotImplementedError("TODO")


def main(argv: list[str]) -> int:
    chemin = Path(argv[1]) if len(argv) > 1 else Path(__file__).parent / "data" / "access.log"

    if len(argv) > 2 and argv[2] == "--follow":
        for ligne in suivre(chemin):
            print(ligne)
        return 0

    print("Top 5 des IP :")
    for ip, n in top_ips(parser(lire_lignes(chemin))):
        print(f"  {ip:16} {n:4}")

    # TODO : répartition des codes, top 5 des IP en erreur (code >= 400),
    #        octets servis par chemin sous /api (top 3).
    # Rappel : un générateur épuisé ne se rembobine pas → reconstruis le pipeline
    # pour chaque agrégation.
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
