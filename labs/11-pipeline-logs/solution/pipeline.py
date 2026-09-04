# solution/pipeline.py — Labo 11 : analyse d'un access.log nginx avec des générateurs.
#
# Rôle : lire data/access.log ligne par ligne, parser chaque ligne en dict,
#        filtrer, agréger, sans jamais charger le fichier entier en mémoire.
# Lancé par : python3 solution/pipeline.py [chemin_du_log]
#
# Architecture = un tube Unix :
#   lire_lignes() | parser() | filtrer_code() | Counter
# Chaque étage est un générateur : il tire une ligne sur l'étage d'avant,
# la transforme, la rend. Rien n'est stocké tant qu'on n'agrège pas.

import functools
import re
import sys
import time
from collections import Counter
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Décorateur @chrono : mesure le temps d'un appel, sans toucher à la fonction.
# ---------------------------------------------------------------------------
def chrono(fonction):
    @functools.wraps(fonction)          # garde __name__ et __doc__ de l'originale
    def enveloppe(*args, **kwargs):
        debut = time.perf_counter()     # horloge haute résolution, monotone
        resultat = fonction(*args, **kwargs)
        duree_ms = (time.perf_counter() - debut) * 1000
        print(f"[chrono] {fonction.__name__} : {duree_ms:.1f} ms", file=sys.stderr)
        return resultat
    return enveloppe


# ---------------------------------------------------------------------------
# 2. Gestionnaire de contexte : ouvre le fichier, signale, et ferme QUOI QU'IL ARRIVE.
#    Équivalent d'un open() avec un message ; l'intérêt est de voir la mécanique
#    avant/yield/après. Le try/finally est indispensable : sans lui, une exception
#    dans le bloc `with` sauterait la fermeture.
# ---------------------------------------------------------------------------
@contextmanager
def fichier_log(chemin: Path):
    print(f"[ouverture] {chemin}", file=sys.stderr)
    f = open(chemin, encoding="utf-8")
    try:
        yield f                          # ce que reçoit le « as f »
    finally:
        f.close()
        print(f"[fermeture] {chemin}", file=sys.stderr)


# ---------------------------------------------------------------------------
# 3. Étage 1 : lire les lignes, une à la fois.
#    Un fichier ouvert est déjà un itérateur de lignes : le for tire dessus
#    sans charger le fichier. On enlève juste le \n final.
# ---------------------------------------------------------------------------
def lire_lignes(chemin: Path) -> Iterator[str]:
    with fichier_log(chemin) as f:
        for ligne in f:
            yield ligne.rstrip("\n")


# ---------------------------------------------------------------------------
# 4. Étage 2 : parser le format "combined" de nginx.
#    203.0.113.42 - - [03/Sep/2026:08:00:10 +0200] "GET /.env HTTP/1.1" 404 15908 "-" "curl/8.7.1"
#    Une regex avec des groupes nommés : (?P<nom>...) → m.group("nom") / m.groupdict().
#    re.compile une seule fois au chargement du module, pas à chaque ligne.
# ---------------------------------------------------------------------------
FORMAT_COMBINED = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<date>[^\]]+)\] '
    r'"(?P<methode>[A-Z]+) (?P<chemin>\S+) [^"]*" '
    r'(?P<code>\d{3}) (?P<taille>\d+) "(?P<referer>[^"]*)" "(?P<agent>[^"]*)"'
)


def parser(lignes: Iterable[str]) -> Iterator[dict]:
    for ligne in lignes:
        m = FORMAT_COMBINED.match(ligne)
        if m is None:                    # ligne corrompue : on l'ignore, on ne plante pas
            continue
        entree = m.groupdict()           # {"ip": ..., "date": ..., ...} tout en str
        entree["code"] = int(entree["code"])      # on convertit ce qui doit l'être
        entree["taille"] = int(entree["taille"])
        yield entree


# ---------------------------------------------------------------------------
# 5. Étage 3 : filtres. Chacun prend un flux de dicts et en rend un sous-ensemble.
#    Le paramètre `minimum` permet filtrer_code(entrees, 400) → erreurs 4xx et 5xx,
#    filtrer_code(entrees, 500) → uniquement les 5xx.
# ---------------------------------------------------------------------------
def filtrer_code(entrees: Iterable[dict], minimum: int, maximum: int = 599) -> Iterator[dict]:
    for e in entrees:
        if minimum <= e["code"] <= maximum:
            yield e


def filtrer_chemin(entrees: Iterable[dict], prefixe: str) -> Iterator[dict]:
    for e in entrees:
        if e["chemin"].startswith(prefixe):
            yield e


# ---------------------------------------------------------------------------
# 6. Agrégations. Ici, et seulement ici, on consomme le flux.
#    Counter est un dict spécialisé : Counter(iterable) compte les occurrences,
#    .most_common(n) rend les n plus fréquents. L'expression génératrice
#    (e["ip"] for e in entrees) ne crée aucune liste intermédiaire.
# ---------------------------------------------------------------------------
@chrono
def top_ips(entrees: Iterable[dict], n: int = 5) -> list[tuple[str, int]]:
    return Counter(e["ip"] for e in entrees).most_common(n)


@chrono
def repartition_codes(entrees: Iterable[dict]) -> Counter:
    return Counter(e["code"] for e in entrees)


@chrono
def octets_par_chemin(entrees: Iterable[dict]) -> Counter:
    total = Counter()
    for e in entrees:
        total[e["chemin"]] += e["taille"]    # Counter accepte += sur une clé absente (0 par défaut)
    return total


# ---------------------------------------------------------------------------
# 7. Bonus : tail -f. Générateur infini qui rend les nouvelles lignes au fur et
#    à mesure qu'elles arrivent. readline() rend "" en fin de fichier (pas
#    d'exception) : on dort un peu et on réessaie. Le curseur du fichier reste
#    où il était, donc la prochaine lecture voit ce qui a été ajouté depuis.
#    À l'arrêt (Ctrl-C), KeyboardInterrupt remonte à travers le générateur
#    et le with ferme le fichier.
# ---------------------------------------------------------------------------
def suivre(chemin: Path, intervalle: float = 0.5) -> Iterator[str]:
    with open(chemin, encoding="utf-8") as f:
        f.seek(0, 2)                     # 2 = depuis la fin : on ne relit pas l'historique
        while True:
            ligne = f.readline()
            if ligne:
                yield ligne.rstrip("\n")
            else:
                time.sleep(intervalle)


# ---------------------------------------------------------------------------
# 8. Point d'entrée. Remarque : chaque agrégation reconstruit son pipeline,
#    parce qu'un générateur épuisé ne se rembobine pas (piège du chapitre 11).
#    Sur un gros fichier, on lirait plutôt une seule fois en alimentant
#    plusieurs Counter dans la même boucle ; c'est le bonus 5 du labo.
# ---------------------------------------------------------------------------
def main(argv: list[str]) -> int:
    chemin = Path(argv[1]) if len(argv) > 1 else Path(__file__).parent.parent / "data" / "access.log"

    if len(argv) > 2 and argv[2] == "--follow":
        for ligne in suivre(chemin):
            print(ligne)
        return 0                         # jamais atteint : on sort par Ctrl-C

    print("Top 5 des IP :")
    for ip, n in top_ips(parser(lire_lignes(chemin))):
        print(f"  {ip:16} {n:4}")

    print("\nRépartition des codes HTTP :")
    codes = repartition_codes(parser(lire_lignes(chemin)))
    for code in sorted(codes):
        print(f"  {code}  {codes[code]:4}")

    print("\nTop 5 des IP en erreur (>= 400) :")
    erreurs = filtrer_code(parser(lire_lignes(chemin)), 400)
    for ip, n in top_ips(erreurs):
        print(f"  {ip:16} {n:4}")

    print("\nOctets servis par chemin (/api seulement, top 3) :")
    api = filtrer_chemin(parser(lire_lignes(chemin)), "/api")
    for chemin_api, octets in octets_par_chemin(api).most_common(3):
        print(f"  {chemin_api:20} {octets:>10}")

    return 0


if __name__ == "__main__":              # exécuté seulement si lancé comme script
    sys.exit(main(sys.argv))            # pas si importé par un test ou un autre module
