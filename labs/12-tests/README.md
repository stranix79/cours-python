# Labo 12 — Tester un module de versions

**Chapitre** : [12. Tester avec pytest](../../cours/12-tests-pytest.md)

## Objectif
Écrire les tests **avant** le code d'un petit module `versions.py` (parser, comparer, incrémenter des versions semver, vérifier une contrainte `^1.2.0`), puis faire passer les tests. Et apprendre la convention de test des labos 12 à 21.

## Consignes
1. Lance `pytest` tel quel. Quatre tests échouent (`NotImplementedError` : deux fonctions, dont une paramétrée en trois cas), sept sont sautés (`skip`). Lis la sortie : c'est ton point de départ, rouge.
2. Complète `parse()` dans `versions.py` jusqu'à ce que les deux premiers tests passent. Vert. Ne fais rien de plus que ce que les tests demandent.
3. Écris les tests marqués `TODO` dans `test_versions.py`, un par un, en enlevant le `@pytest.mark.skip`. Pour chacun : lance `pytest`, constate l'échec, complète `versions.py`, constate le succès. `pytest -x` s'arrête au premier échec, `pytest --lf` ne relance que ceux qui ont échoué.
4. `test_compatible` doit être paramétré avec au moins dix cas couvrant `^`, `~`, l'égalité, `>=`, `<`, et une contrainte double `>=1.2.0,<2.0.0`. Pense aux cas limites : `2.0.0` n'est pas dans `^1.2.0`, `1.3.0` n'est pas dans `~1.2.0`.
5. Vérifie ta suite contre la solution : `SOLUTION=1 pytest`. Si un de tes tests échoue contre la solution, c'est soit ton test qui est faux, soit un cas que la solution n'a pas prévu : ouvre `solution/versions.py` et tranche.
6. Bonus : ajoute un doctest dans la docstring de `bump` et lance `python3 -m doctest -v versions.py`.

## Comment lancer
```bash
source ../../.venv/bin/activate
pytest                          # tes tests contre ton squelette
pytest -v                       # un nom par test, avec les cas paramétrés
pytest -x --lf                  # stop au premier échec, seulement les derniers échoués
SOLUTION=1 pytest               # tes tests contre solution/versions.py
SOLUTION=1 pytest solution/     # les tests de la solution contre la solution (35 tests)
```

Convention pour tous les labos suivants : `pytest.ini` met pytest en mode `importlib` et `conftest.py` place `solution/` en tête de `sys.path` quand `SOLUTION=1`. Donc `pytest` teste ton code, `SOLUTION=1 pytest` teste la solution, sans rien copier.

## Pour aller plus loin
- `pip install pytest-cov` puis `SOLUTION=1 pytest --cov=versions --cov-report=term-missing solution/` : quelles lignes de `versions.py` ne sont couvertes par aucun test ?
- Ajoute la gestion des préversions (`1.2.3-beta.1 < 1.2.3`) : c'est la partie de semver qui fait pleurer tout le monde. Commence par les tests.
- Le module `packaging.version` (installé avec pip) fait tout ça pour de vrai, avec les règles PEP 440 de Python. Compare son comportement au tien dans le REPL.
