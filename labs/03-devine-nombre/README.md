# Labo 03 — Devine le nombre, FizzBuzz, et des logs nginx

**Chapitre** : [3. Contrôle : conditions et boucles](../../cours/03-controle-conditions-boucles.md)

## Objectif
Boucles `while` et `for`, conditions, `break`, et un premier `match` sur des données réelles : des lignes de log nginx.

## Consignes
1. Complète `devine.py` : le programme tire un nombre entre 1 et 100 (`random.randint(1, 100)`), puis demande des propositions en boucle jusqu'à ce que l'utilisateur trouve. À chaque tour : « Trop grand », « Trop petit » ou « Gagné en N essais ». Une proposition qui n'est pas entre 1 et 100 ne compte pas comme un essai.
2. Ajoute une limite : au bout de 7 essais, « Perdu, c'était 42 ». Utilise le `else` de la boucle `while` (exécuté si on sort sans `break`) pour afficher ce message.
3. Complète `fizzbuzz.py` : pour i de 1 à 30, `FizzBuzz` si divisible par 15, `Fizz` par 3, `Buzz` par 5, sinon le nombre. Un résultat par ligne. Vérifie : `python3 fizzbuzz.py | diff - solution/attendu.txt` ne doit rien afficher.
4. Bonus : réécris FizzBuzz sans aucun `if` : construis la chaîne avec `"Fizz" * (i % 3 == 0) + "Buzz" * (i % 5 == 0)` puis `or i`. Comprends pourquoi ça marche (chapitre 3.3 : `and`/`or` renvoient un opérande, `True * "Fizz"` vaut `"Fizz"`).
5. Bonus 2 : complète `logs.py`. Il contient une liste de lignes de log nginx en dur. Pour chaque ligne, `split()` la coupe en mots ; avec un `match` sur la liste de mots, extrais l'IP, la méthode HTTP, le chemin et le code de statut, puis affiche une ligne par requête et, à la fin, le nombre de codes 2xx, 4xx et 5xx. Une ligne qui ne colle pas au motif est signalée comme « ligne ignorée ».

## Comment lancer
```bash
source ../../.venv/bin/activate    # si ce n'est pas déjà fait
python3 devine.py
python3 fizzbuzz.py | diff - solution/attendu.txt && echo OK
python3 logs.py
python3 solution/devine.py         # les solutions
python3 solution/fizzbuzz.py
python3 solution/logs.py
```

## Sortie attendue (logs.py)
```
203.0.113.7      GET     /index.html                    200
203.0.113.7      GET     /style.css                     200
198.51.100.23    POST    /api/login                     401
203.0.113.7      GET     /favicon.ico                   404
ligne ignorée : garbage line that does not parse
198.51.100.23    GET     /api/users                     500
2xx : 2   4xx : 2   5xx : 1
```

## Pour aller plus loin
- `random.seed(42)` avant le tirage rend le jeu reproductible : pratique pour tester. Cherche pourquoi un générateur pseudo-aléatoire est déterministe.
- Le `match` sur `split()` est fragile (un chemin avec un espace casse tout). Le vrai outil pour parser des logs est le module `re` (expressions régulières) : `re.match(r'(\S+) .* "(\S+) (\S+) \S+" (\d{3})', ligne)`. Essaie-le dans le REPL sur une ligne.
- FizzBuzz en assembleur ARM64 : [asm-m1, labo 05](https://github.com/stranix79/asm-m1). Même problème, sans `print`.
