# solution/gil_demo.py — Labo 10 : le GIL mesuré.
#
# Rôle : montrer que deux threads ne vont pas plus vite qu'un seul sur du
#        calcul pur (le GIL ne laisse qu'un thread exécuter du bytecode à la
#        fois), alors que deux processus, chacun avec son interpréteur et son
#        GIL, tournent vraiment en parallèle.
# Lancé par : python3 solution/gil_demo.py
#
# Résultat typique sur un M1 (3.13) :
#   séquentiel 0.24s | 2 threads 0.25s | 2 processus 0.18s
# Les threads : même temps (ils se relaient sur le verrou, plus un peu de
# frais de bascule). Les processus : plus rapide, mais pas 2× : il faut
# démarrer deux interpréteurs (spawn sur macOS) et sérialiser les arguments
# et les résultats (pickle) pour les faire passer d'un processus à l'autre.
# Avec N plus grand, le gain tend vers 2×.
#
# Si le calcul était remplacé par du temps d'attente (time.sleep, une requête
# HTTP, une lecture disque), les threads gagneraient aussi : un thread qui
# attend relâche le GIL. C'est le cas d'usage des threads en Python, et encore
# mieux d'asyncio (chapitre 15).

import multiprocessing as mp
import threading
import time


def cpu(n):
    s = 0
    for i in range(n):
        s += i * i
    return s


# Sur macOS et Windows, multiprocessing démarre les processus enfants par
# « spawn » : un interpréteur neuf qui RÉIMPORTE ce fichier pour retrouver la
# fonction cpu. Sans le garde-fou ci-dessous, l'enfant relancerait tout le
# script, y compris la création d'un Pool, à l'infini. Sur Linux (fork), on
# s'en sort sans, mais le garde-fou reste la bonne habitude.
if __name__ == "__main__":
    N = 3_000_000

    t0 = time.perf_counter()
    cpu(N); cpu(N)
    t1 = time.perf_counter()

    threads = [threading.Thread(target=cpu, args=(N,)) for _ in range(2)]
    t2 = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    t3 = time.perf_counter()

    with mp.Pool(2) as pool:           # deux interpréteurs enfants
        t4 = time.perf_counter()
        pool.map(cpu, [N, N])          # arguments et résultats voyagent en pickle
        t5 = time.perf_counter()

    print(f"séquentiel {t1 - t0:.2f}s | 2 threads {t3 - t2:.2f}s | 2 processus {t5 - t4:.2f}s")
