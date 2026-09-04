# Labo 04 — Inventaire de serveurs

**Chapitre** : [4. Collections : listes, tuples, dicts, sets](../../cours/04-collections.md)

## Objectif
Poser à une liste de dicts les questions qu'on pose à un inventaire (qui, combien, par quoi, en double ?) en choisissant à chaque fois la bonne structure : compréhension, `sorted` avec clé, `Counter`, `defaultdict`, `set`.

## Consignes
1. Complète `inventaire.py`, étape par étape. Chaque étape a son `# TODO` et la ligne d'affichage est déjà écrite en commentaire : décommente-la quand ta variable existe.
2. Étapes 1 à 3 : filtrer les serveurs web, trier par RAM décroissante puis nom, sommer la RAM. Une compréhension, un `sorted(key=…)`, un `sum()`.
3. Étapes 4 et 5 : compter les serveurs par OS avec `Counter`, puis regrouper les noms par OS avec `defaultdict(list)`.
4. Étape 6 : trouver les doublons de nom avec deux `set`. Réfléchis à pourquoi une liste serait une mauvaise idée pour `vus` si l'inventaire avait 100 000 lignes.
5. Bonus : reconstruire une liste de dicts à partir d'une chaîne CSV avec `splitlines`, `split`, `zip`, `dict`. La dernière ligne doit afficher `True`.
6. Bonus 2 : dans le REPL (`python3 -i inventaire.py`), fais `copie = SERVEURS` puis `copie[0]["ram"] = 999`. Regarde `SERVEURS[0]`. Puis essaie avec `copie = SERVEURS.copy()` : même résultat ? Pourquoi ? (Réponse au chapitre 10.)

## Comment lancer
```bash
source ../../.venv/bin/activate    # si ce n'est pas déjà fait
python3 inventaire.py
python3 solution/inventaire.py
```

## Sortie attendue
```
Serveurs web : ['web1', 'web2', 'web1']
Par RAM décroissante :
  db1       64 Go
  db2       64 Go
  mon1      32 Go
  web1      16 Go
  web1      16 Go
  web2      16 Go
  cache1     8 Go
  lb1        4 Go
RAM totale : 220 Go
Serveurs par OS :
  debian   4
  rhel     3
  alpine   1
Noms par OS :
  alpine   cache1
  debian   web1, web2, lb1, web1
  rhel     db1, db2, mon1
Doublons : ['web1']
CSV == inventaire : True
```

## Pour aller plus loin
- `sorted(SERVEURS, key=lambda s: s["ram"])` puis `key=itemgetter("ram")` avec `from operator import itemgetter` : même résultat, et `itemgetter("ram", "nom")` renvoie directement un tuple pour un tri multiple.
- Une liste de dicts, c'est aussi ce qu'Ansible manipule dans `hostvars`. Regarde le résultat de `ansible-inventory --list` sur un inventaire à toi : c'est du JSON, donc des dicts et des listes imbriqués.
- Mesure : `python3 -m timeit -s "l = list(range(100000)); s = set(l)" "99999 in l"` puis la même chose avec `"99999 in s"`. C'est la différence entre O(n) et O(1).
