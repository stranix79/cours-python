# Labo 15 — Vérificateur de disponibilité : séquentiel, threads, asyncio

**Chapitre** : [15. Asynchrone : asyncio, async/await](../../cours/15-async.md)

## Objectif
Écrire trois fois le même vérificateur d'URLs (séquentiel, `ThreadPoolExecutor`, `asyncio` avec sémaphore), les chronométrer sur un serveur local volontairement lent, et les tester sans réseau avec `pytest-asyncio`.

## Consignes
1. Dans un second terminal, lance le serveur lent : `python3 serveur_lent.py`. Vérifie avec `curl http://127.0.0.1:8000/site/1` (deux fois : le délai est le même pour la même URL). Lis `serveur_lent.py` : pourquoi `ThreadingHTTPServer` et pas `HTTPServer` ?
2. Complète `lire_urls()`, `verifier()` et `verifier_sequentiel()` dans `dispo.py`. Contrat : une erreur réseau devient un `Resultat` avec `statut=None`, jamais une exception. `pytest -k "lire or verifier_ne or sequentiel"` doit passer. Lance `python3 dispo.py --mode seq --detail` : environ 9 s pour 20 URLs.
3. Complète `verifier_threads()` avec un `ThreadPoolExecutor`. Sans toucher à `verifier()`. `python3 dispo.py --mode threads` : environ 1 s.
4. Complète `verifier_async()`, `verifier_tout_async()` (un `TaskGroup` ou `gather`, un `Semaphore(limite)`) et `verifier_asyncio()`. `pytest` doit être tout vert, y compris `test_le_semaphore_borne_la_concurrence`. Puis `python3 dispo.py --mode tous`, et joue avec `--limite 2`, `--limite 20` : explique les temps que tu observes.
5. Ajoute `http://127.0.0.1:8000/timeout` à `urls.txt` et relance avec `--timeout 2`. Que rend chaque stratégie pour cette URL ? Combien de temps ça coûte au total dans chaque mode ?
6. Bonus : dans `verifier_async()`, remplace `await client.get(url)` par `client.get(url)` (sans `await`) et lance `python3 -W error dispo.py --mode async`. Lis l'erreur. Bonus 2 : ajoute un mode `--mode process` avec `ProcessPoolExecutor` : est-ce plus rapide ? Pourquoi non ?

## Comment lancer
```bash
source ../../.venv/bin/activate
python3 serveur_lent.py                  # terminal 2, laisse tourner
pytest                                   # tes tests (sans réseau, sans serveur)
SOLUTION=1 pytest                        # les mêmes tests sur la solution
python3 dispo.py --mode tous --detail    # les trois stratégies chronométrées
python3 solution/dispo.py --limite 20    # la solution
```

Sortie attendue (les temps varient un peu) :
```
20 URLs, limite 10, timeout 5 s
--- séquentiel :  8.94 s
--- threads    :  1.13 s
--- asyncio    :  1.25 s
18/20 disponibles
```
Le code de retour est 1 dès qu'une URL est indisponible (`echo $?`), pour un cron ou un healthcheck.

## Pour aller plus loin
- Remplace `serveur_lent.py` par une vraie liste de vingt sites publics dans `urls.txt` : les écarts entre stratégies sont-ils les mêmes ? (Attention au DNS : la première résolution coûte, les suivantes sont en cache.)
- `python3 -X importtime dispo.py --mode seq 2>&1 | sort -t'|' -k2 -n | tail -5` : combien coûte l'import d'`httpx` et d'`asyncio` au démarrage ?
- Lis le code de `asyncio.Semaphore` dans la stdlib (`python3 -c "import asyncio.locks, inspect; print(inspect.getsource(asyncio.locks.Semaphore))"`) : une file de futures et un compteur, rien de plus.
