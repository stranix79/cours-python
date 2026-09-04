# gil_demo.py — Labo 10 : le même calcul en séquence, en threads, en processus.
#
# Lance : python3 gil_demo.py
# Prédiction : les 2 threads vont-ils diviser le temps par deux ? Et les 2 processus ?
#
# Ce fichier est identique dans solution/ (avec l'explication) : il n'y a rien
# à compléter, seulement à prédire puis à comprendre.

import multiprocessing as mp
import threading
import time


def cpu(n):
    s = 0
    for i in range(n):
        s += i * i
    return s


if __name__ == "__main__":       # obligatoire avec multiprocessing (voir solution)
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

    with mp.Pool(2) as pool:
        t4 = time.perf_counter()
        pool.map(cpu, [N, N])
        t5 = time.perf_counter()

    print(f"séquentiel {t1 - t0:.2f}s | 2 threads {t3 - t2:.2f}s | 2 processus {t5 - t4:.2f}s")
