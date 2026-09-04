# convertisseur.py — Labo 02 : températures, tailles, durées.
# Trois conversions demandées au clavier, trois affichages formatés.

# --- 1. Température --------------------------------------------------------
reponse = input("Température en °C ? ")
celsius = float(reponse)          # input() renvoie une str : on convertit

# TODO : calcule fahrenheit = celsius * 9 / 5 + 32
#        et affiche « 20.0 °C = 68.0 °F » avec une décimale ({x:.1f})

# --- 2. Taille en octets ---------------------------------------------------
taille = int(input("Taille en octets ? "))

# TODO : affiche la taille « lisible » : o, Kio, Mio, Gio, Tio
#   - on divise par 1024 tant que la valeur est >= 1024
#   - une décimale : 1536 → « 1.5 Kio », 3221225472 → « 3.0 Gio »
#   - indice : une variable valeur (float) et une variable unite (str)

# TODO : affiche « hexa : 0x... » ({taille:#x}) et « binaire : ... » sur 32 bits ({taille:032b})

# --- 3. Durée --------------------------------------------------------------
secondes = int(input("Durée en secondes ? "))

# TODO : affiche « 3725 s = 1:02:05 »
#   - heures, reste = divmod(secondes, 3600)
#   - minutes, sec = divmod(reste, 60)
#   - deux chiffres pour minutes et secondes : {minutes:02d}
