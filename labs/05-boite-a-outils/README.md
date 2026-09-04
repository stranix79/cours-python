# Labo 05 — Boîte à outils DevOps

**Chapitre** : [5. Fonctions](../../cours/05-fonctions.md)

## Objectif
Écrire quatre fonctions réutilisables, avec arguments nommés, valeurs par défaut, docstrings et type hints, dont une qui reçoit une fonction en paramètre.

## Consignes
1. Complète `outils.py` : `taille_lisible(octets, decimales=1)` renvoie `"1.5 Ko"`, `"2.0 Mo"`… (base 1024, unités o, Ko, Mo, Go, To). `taille_lisible(0)` donne `"0 o"` et un entier en dessous de 1024 s'affiche sans décimale.
2. `parse_kv(texte, sep=" ")` transforme `"host=web01 port=22"` en `{"host": "web01", "port": "22"}`. Bonus : convertis en `int` les valeurs qui en sont (`str.isdigit`). Une valeur sans `=` est ignorée.
3. `slugify(texte)` transforme `"Serveur Web #1 (prod)"` en `"serveur-web-1-prod"` : minuscules, tout ce qui n'est pas lettre ou chiffre devient un tiret, pas de tirets doubles ni aux extrémités. Indice : `str.isalnum()`, `str.strip("-")`.
4. `retry(fonction, essais=3, attente=0.0)` **appelle** `fonction()` jusqu'à ce qu'elle réussisse, au plus `essais` fois, en attendant `attente` secondes entre deux (`time.sleep`). Si elle réussit, renvoie son résultat ; si toutes les tentatives lèvent une exception, relance la dernière (`raise`). Teste-la avec la fonction `instable()` fournie, qui échoue deux fois puis réussit.
5. Le bloc `if __name__ == "__main__":` en bas fait une démo de chaque fonction. Lance `python3 outils.py` et compare avec la sortie attendue ci-dessous. Ce bloc ne s'exécute que quand le fichier est lancé directement, pas quand il est importé : c'est le sujet du chapitre 6. Vérifie-le dans le REPL : `python3 -i -c "import outils"` puis `outils.slugify("Hello World")`.
6. Bonus : rends `retry` capable de recevoir des arguments pour la fonction : `retry(fonction, *args, essais=3, **kwargs)`.

## Sortie attendue
```
$ python3 outils.py
1536 octets      → 1.5 Ko
10485760 octets  → 10.0 Mo
{'host': 'web01', 'port': 22, 'user': 'root'}
serveur-web-1-prod
instable : échec 1
instable : échec 2
instable : ok
```

## Comment lancer
```bash
source ../../.venv/bin/activate    # si ce n'est pas déjà fait
python3 outils.py
python3 solution/outils.py
python3 -i -c "import outils"      # puis : help(outils), outils.taille_lisible(2**40)
```

## Pour aller plus loin
- `help(outils)` dans le REPL affiche toutes les docstrings du module. C'est ce que lisent les gens qui utilisent ton code, et ton éditeur.
- Ajoute des type hints partout et lance `mypy outils.py` (installé dans le `.venv`) : il te signalera un appel `taille_lisible("abc")` avant même de lancer le script.
- `functools.partial(retry, essais=5)` fabrique une nouvelle fonction avec un défaut différent. Cherche ce que fait `partial` : c'est une closure toute faite.
