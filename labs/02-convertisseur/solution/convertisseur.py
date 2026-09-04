# solution/convertisseur.py — Labo 02 : températures, tailles, durées.
#
# Rôle : demander trois valeurs au clavier et les afficher converties.
# Lancé par : python3 solution/convertisseur.py (rien ne l'importe).
#
# Tout ce qui sort d'input() est une str. La première chose à faire est donc
# de convertir : float() pour une valeur à virgule, int() pour un entier.
# En C on aurait fait scanf("%f", &c) ; ici la lecture et la conversion sont
# deux étapes séparées, et la conversion plante (ValueError) si le texte n'est
# pas un nombre. On verra au chapitre 8 comment attraper ça proprement.

# --- 1. Température --------------------------------------------------------
reponse = input("Température en °C ? ")
# Bonus 5 : on tolère la virgule à la française. replace() renvoie une
# nouvelle chaîne (les str sont immuables), on la passe directement à float().
celsius = float(reponse.replace(",", "."))

# 9 / 5 vaut 1.8 : en Python, / donne toujours un float, même entre entiers.
# (En C, 9 / 5 aurait donné 1 et la conversion aurait été fausse.)
fahrenheit = celsius * 9 / 5 + 32
print(f"{celsius:.1f} °C = {fahrenheit:.1f} °F")

# --- 2. Taille en octets ---------------------------------------------------
taille = int(input("Taille en octets ? "))

# On garde une copie en float pour diviser sans perdre les décimales,
# et on parcourt les unités dans l'ordre. Le while est présenté au chapitre 3 ;
# la version « cascade de if » est en commentaire plus bas pour comparaison.
valeur = float(taille)
unite = "o"
for suivante in ("Kio", "Mio", "Gio", "Tio"):
    if valeur < 1024:
        break                     # on a trouvé la bonne unité, on s'arrête
    valeur = valeur / 1024
    unite = suivante

# Version sans boucle, équivalente (jusqu'à Gio) :
# if taille >= 1024 ** 3:
#     valeur, unite = taille / 1024 ** 3, "Gio"
# elif taille >= 1024 ** 2:
#     valeur, unite = taille / 1024 ** 2, "Mio"
# elif taille >= 1024:
#     valeur, unite = taille / 1024, "Kio"

print(f"{taille} octets = {valeur:.1f} {unite}")

# #x ajoute le préfixe 0x ; 032b remplit à gauche avec des zéros sur 32 chiffres.
# Si la taille dépasse 2**32, le binaire aura simplement plus de 32 chiffres :
# un int Python n'a pas de largeur fixe, le format ne tronque jamais.
print(f"  hexa : {taille:#x}   binaire : {taille:032b}")

# --- 3. Durée --------------------------------------------------------------
secondes = int(input("Durée en secondes ? "))

# divmod(a, b) renvoie le tuple (a // b, a % b) : quotient et reste d'un coup.
# L'affectation à deux noms « dépaquette » le tuple (unpacking, chapitre 4).
heures, reste = divmod(secondes, 3600)
minutes, sec = divmod(reste, 60)

# 02d : entier (d) sur 2 positions, complété par des zéros. Sans lui,
# 1:2:5 au lieu de 1:02:05.
print(f"{secondes} s = {heures}:{minutes:02d}:{sec:02d}")
