# Labo 02 — Convertisseur d'unités

**Chapitre** : [2. Variables, types, chaînes](../../cours/02-variables-types-chaines.md)

## Objectif
Manipuler nombres, conversions et f-strings sur trois conversions qu'un DevOps fait de tête toute la journée : températures, tailles en octets, durées en secondes.

## Consignes
1. Complète `convertisseur.py` : le script demande une température en °C avec `input()`, la convertit en °F (`F = C × 9/5 + 32`) et l'affiche avec une décimale : `20.0 °C = 68.0 °F`.
2. Demande ensuite une taille en octets et affiche-la « lisible », comme `df -h` : on divise par 1024 tant que c'est plus grand que 1024, en passant de o à Kio, Mio, Gio, Tio. `1536` doit donner `1.5 Kio`, `3221225472` doit donner `3.0 Gio`. Utilise `while` seulement si tu l'as déjà vu ; sinon, une cascade de tests `if` fait l'affaire (c'est le chapitre 3 qui introduit les boucles proprement).
3. Demande un nombre de secondes et affiche une durée `h:mm:ss` : `3725` donne `1:02:05`. Indices : `divmod(secondes, 3600)` donne les heures et le reste ; `divmod(reste, 60)` donne les minutes et les secondes ; `{m:02d}` formate sur deux chiffres avec un zéro devant.
4. Affiche aussi la taille en hexadécimal et en binaire sur 32 bits avec zéros devant (`{n:#x}`, `{n:032b}`).
5. Bonus : `input()` renvoie une `str`. Que se passe-t-il si tu tapes `abc` à la place d'un nombre ? Lis le traceback. Et si tu tapes `20,5` avec une virgule à la française ? Corrige en remplaçant la virgule par un point avant de convertir.
6. Bonus 2 : dans le REPL, `python3 -i convertisseur.py`, puis tape `f"{taille:e}"` et `f"{taille:,}"`. Et `0.1 + 0.2 == 0.3`.

## Comment lancer
```bash
source ../../.venv/bin/activate    # si ce n'est pas déjà fait
python3 convertisseur.py
python3 solution/convertisseur.py
printf '20\n3221225472\n3725\n' | python3 solution/convertisseur.py    # sans taper
```

## Sortie attendue
```
Température en °C ? 20
20.0 °C = 68.0 °F
Taille en octets ? 3221225472
3221225472 octets = 3.0 Gio
  hexa : 0xc0000000   binaire : 11000000000000000000000000000000
Durée en secondes ? 3725
3725 s = 1:02:05
```

## Pour aller plus loin
- `round(2.675, 2)` donne `2.67`, pas `2.68`. `f"{2.675:.20f}"` te montre pourquoi.
- La stdlib a `datetime.timedelta(seconds=3725)` qui affiche `1:02:05` tout seul. Cherche sa doc avec `help(datetime.timedelta)` : tu verras que ce que tu viens d'écrire à la main est exactement ce que la stdlib fait aussi.
