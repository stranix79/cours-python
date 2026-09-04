# Labo 14 — Client de l'API GitHub

**Chapitre** : [14. HTTP et APIs, côté client](../../cours/14-http-et-apis-cote-client.md)

## Objectif
Écrire un vrai client d'API : pagination par l'en-tête `Link`, en-têtes, timeout, erreurs séparées (HTTP / réseau), secret dans l'environnement, mode hors ligne, et des tests qui ne touchent jamais le réseau grâce à `httpx.MockTransport`.

## Consignes
1. Lis `test_github_repos.py` : le faux GitHub (`faux_github`) renvoie deux pages reliées par un en-tête `Link`, puis un 404. C'est le contrat que ton code doit respecter. Lance `pytest` : tout échoue, c'est normal.
2. Complète `creer_client()` et `lister_depots()` dans `github_repos.py` : suis la pagination avec `resp.links["next"]["url"]` tant qu'il y en a une. `pytest -k lister` doit passer.
3. Complète `charger_offline()`, `compter_langages()` (les `language: null` regroupés sous `(aucun)`, tri décroissant) et `formater_tableau()` (tri par `pushed_at` décroissant, colonnes alignées). `pytest` doit être tout vert.
4. Complète le `main()` : attrape `httpx.HTTPStatusError` (code 1), `httpx.TimeoutException` et `httpx.ConnectError` (code 2) séparément, avec un message utile. Teste en vrai : `python3 github_repos.py stranix79`, puis avec un utilisateur inexistant, puis `--base-url http://127.0.0.1:9` (rien n'écoute : ConnectError).
5. Exporte un `GITHUB_TOKEN` (Settings → Developer settings → Personal access tokens, aucune permission nécessaire pour du public) et vérifie avec `--json | head` que ça marche toujours. Sans token tu as 60 requêtes par heure, avec 5 000.
6. Bonus : ajoute une option `--langage Python` qui filtre le tableau, et un test pour elle. Bonus 2 : ajoute une fonction `get_avec_retries()` (backoff exponentiel, section 14.7) et un test avec un `MockTransport` qui répond 503 deux fois puis 200.

## Comment lancer
```bash
source ../../.venv/bin/activate
pytest                                   # tes tests (sans réseau)
SOLUTION=1 pytest                        # les mêmes tests sur la solution
python3 github_repos.py --offline        # data/repos.json, sans réseau
python3 github_repos.py stranix79        # en vrai
python3 solution/github_repos.py stranix79 --json | head -20
```

Sortie attendue de `--offline` (tronquée) :
```
dépôt                                            langage        ★  dernier push
-------------------------------------------------------------------------------
asm-m1                                           Assembly       0  2026-09-04
dyndns-cloudflare                                Python         0  2026-09-02
...
13 dépôts, par langage :
  (aucun)        4
  Python         3
```

## Pour aller plus loin
- `data/repos.json` a été produit par `python3 solution/github_repos.py stranix79 --json` puis réduit aux champs utiles. Régénère-le pour ton propre compte.
- Remplace `httpx` par `requests` dans une copie : qu'est-ce qui change ? (`Session`, `r.links`, les noms d'exceptions). Puis par `urllib.request` : combien de lignes en plus ?
- Regarde `python3 -c "import httpx; help(httpx.MockTransport)"` et la doc des transports : c'est le même mécanisme qui sert à tester une API FastAPI sans la lancer (chapitre 19).
