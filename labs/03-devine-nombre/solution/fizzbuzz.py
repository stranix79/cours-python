# solution/fizzbuzz.py — Labo 03 : FizzBuzz de 1 à 30, deux versions.
#
# Rôle : afficher FizzBuzz, une valeur par ligne.
# Lancé par : python3 solution/fizzbuzz.py

# --- Version 1 : la cascade de conditions, dans le bon ordre -----------------
# L'ordre compte : si on testait % 3 en premier, 15 donnerait « Fizz »
# et on n'atteindrait jamais le cas FizzBuzz.
for i in range(1, 31):            # 1 inclus, 31 exclu → 1..30
    if i % 15 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)

# --- Version 2 (bonus) : sans aucun if ---------------------------------------
# Deux idées du chapitre 3 :
#   - bool est un int : (i % 3 == 0) vaut True ou False, soit 1 ou 0,
#     et "Fizz" * 1 donne "Fizz", "Fizz" * 0 donne "" (chaîne vide).
#   - `or` renvoie son premier opérande s'il est vrai, sinon le second :
#     "" or i  →  i   (la chaîne vide est fausse),  "Fizz" or i  →  "Fizz".
# On l'active en passant un argument quelconque : python3 fizzbuzz.py bonus
import sys
if len(sys.argv) > 1:
    print("--- version sans if ---")
    for i in range(1, 31):
        print("Fizz" * (i % 3 == 0) + "Buzz" * (i % 5 == 0) or i)
