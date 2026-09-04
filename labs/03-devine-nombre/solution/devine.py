# solution/devine.py — Labo 03 : le jeu « devine le nombre », version commentée.
#
# Rôle : tirer un nombre, laisser l'utilisateur le deviner en 7 essais maximum.
# Lancé par : python3 solution/devine.py

import random

MAX_ESSAIS = 7
# randint(a, b) inclut les deux bornes, contrairement à range(a, b).
# C'est une des rares fonctions de la stdlib où la fin est incluse.
secret = random.randint(1, 100)
essais = 0

print(f"J'ai choisi un nombre entre 1 et 100. Tu as {MAX_ESSAIS} essais.")

while essais < MAX_ESSAIS:
    proposition = int(input("Ta proposition ? "))

    # Comparaison chaînée : équivaut à  1 <= proposition and proposition <= 100.
    if not 1 <= proposition <= 100:
        print("Entre 1 et 100, s'il te plaît.")
        continue                  # retour au while, sans passer par essais += 1

    essais += 1

    if proposition > secret:
        print("Trop grand.")
    elif proposition < secret:
        print("Trop petit.")
    else:
        print(f"Gagné en {essais} essai(s) !")
        break                     # sort du while ET saute le else ci-dessous
else:
    # Ce else appartient au while, pas au if : il s'exécute uniquement si
    # la boucle s'est terminée « naturellement », c'est-à-dire parce que la
    # condition essais < MAX_ESSAIS est devenue fausse, sans break.
    # En C on aurait eu besoin d'un booléen  int gagne = 0;  testé après la boucle.
    print(f"Perdu, c'était {secret}.")
