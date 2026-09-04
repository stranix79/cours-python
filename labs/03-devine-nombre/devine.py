# devine.py — Labo 03 : le jeu « devine le nombre ».
# L'ordinateur tire un nombre entre 1 et 100, l'utilisateur le devine.

import random

MAX_ESSAIS = 7
secret = random.randint(1, 100)   # entier entre 1 et 100 inclus
essais = 0

print(f"J'ai choisi un nombre entre 1 et 100. Tu as {MAX_ESSAIS} essais.")

# TODO : boucle while tant que essais < MAX_ESSAIS
#   - lire une proposition avec input(), la convertir en int
#   - si elle n'est pas entre 1 et 100 : message, et on recommence SANS compter
#     l'essai (continue)
#   - essais += 1
#   - comparer à secret : « Trop grand », « Trop petit », ou
#     « Gagné en N essais » suivi de break
# TODO : clause else du while : « Perdu, c'était {secret} »
