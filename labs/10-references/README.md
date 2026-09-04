# Labo 10 — Prédire, puis vérifier

**Chapitre** : [10. Sous le capot : références, mémoire, GIL, bytecode](../../cours/10-sous-le-capot.md)

## Objectif
Dix expériences courtes sur le modèle mémoire de Python. Pour chacune, tu écris ta prédiction **avant** de lancer. Le but n'est pas d'avoir bon, c'est de savoir pourquoi.

## Consignes
1. Ouvre `predictions.py`. Pour chaque expérience, remplis le commentaire `# Prédiction :` avec ce que tu attends (valeurs, `True`/`False`, ordre de rapidité). Ne lance rien avant d'avoir tout rempli.
2. Lance `python3 predictions.py`. Pour chaque écart entre ta prédiction et le résultat, relis la section du chapitre indiquée entre parenthèses, et écris en une ligne, à côté de ta prédiction, pourquoi tu t'étais trompé.
3. Expérience 9 : compte les instructions de bytecode de `moyenne`, puis ajoute une variable locale `n = len(valeurs)` et relance. Qu'est-ce qui change ? Pourquoi `sum` et `len` sont en `LOAD_GLOBAL` et `valeurs` en `LOAD_FAST` ?
4. Expérience 10 : remplace `sum([i for i in range(N)])` par `sum(i for i in range(N))` (sans crochets, chapitre 11). Plus rapide ou plus lent ? Puis fais varier `N` : le rapport entre `boucle` et `builtin` change-t-il ?
5. Bonus 11 : appelle `strlen` de la libc via `ctypes`, d'abord avec `argtypes`/`restype` déclarés, puis sans, en passant un `str` au lieu de `bytes`. Explique le résultat.
6. Bonus 12 : lance `gil_demo.py`. Prédis les trois temps, puis explique-les. Remplace le corps de `cpu` par `time.sleep(0.2)` (même nombre d'appels) et relance : les threads gagnent-ils cette fois ? Pourquoi ?
7. Compare avec `solution/predictions.py`, qui donne chaque réponse et son explication.

## Comment lancer
```bash
source ../../.venv/bin/activate
python3 predictions.py
python3 gil_demo.py
python3 solution/predictions.py
python3 solution/gil_demo.py
```

Ordres de grandeur attendus (un M1, Python 3.13 ; les temps varient d'une machine à l'autre, pas les rapports) :
```
--- 10. Mesurer (10.8)
boucle     5.65 ms
builtin    2.46 ms
compr      4.87 ms
séquentiel 0.25s | 2 threads 0.25s | 2 processus 0.19s
```

## Pour aller plus loin
- `python3 -X importtime -c "import json"` et `python3 -m cProfile -s cumtime predictions.py` : les deux outils de profilage qu'il faut connaître avant de parler de performance.
- `tracemalloc` (stdlib) montre où la mémoire est allouée, ligne par ligne. Essaie-le sur l'expérience 10 avec `compr` : la liste intermédiaire pèse plusieurs mégaoctets.
- Si tu as un `python3.13t` sous la main (`brew install python-freethreading` ou `uv python install 3.13t`), relance `gil_demo.py` avec : les deux threads devraient enfin diviser le temps par deux.
