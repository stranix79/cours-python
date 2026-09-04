# Labo 01 — Hello, et lire un traceback

**Chapitre** : [1. Installer, outiller, lancer](../../cours/01-installer-et-outiller.md)

## Objectif
Vérifier que ta chaîne d'outils marche (Python 3.11+, `.venv`, éditeur), écrire un premier script, et apprendre à lire un traceback sans paniquer.

## Consignes
1. À la racine du dépôt, crée et active le `.venv`, installe `requirements.txt` (voir le [README](../../README.md)). `which python` doit pointer dans `.venv/bin`.
2. Complète `hello.py` : il doit afficher un salut avec ton nom, la version de Python, le système d'exploitation et le nombre de secondes écoulées depuis le 1er janvier 1970 (`time.time()`), arrondi à l'entier.
3. Lance-le : `python3 hello.py`. Puis lance-le depuis le REPL : `python3 -i hello.py` te laisse dans l'interpréteur *après* l'exécution, avec toutes les variables du script sous la main. Tape `nom`, puis `dir()`.
4. Provoque une erreur : remplace `time.time()` par `time.tim()` et relance. Lis le traceback de bas en haut : quel type d'erreur, quelle ligne, quelle suggestion ?
5. Compare avec `solution/hello.py`, qui fait la même chose en expliquant chaque ligne.

## Comment lancer
```bash
source ../../.venv/bin/activate    # si ce n'est pas déjà fait
python3 hello.py
python3 solution/hello.py
```

## Pour aller plus loin
- `python3 -m this` affiche le *Zen of Python*, dix-neuf phrases qui résument la philosophie du langage. Tu les recroiseras.
- `python3 -X importtime -c "import platform" 2>&1 | tail -5` montre le temps que prend chaque import. Utile plus tard pour savoir pourquoi un script met deux secondes à démarrer.
