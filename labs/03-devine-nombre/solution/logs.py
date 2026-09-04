# solution/logs.py — Labo 03 (bonus) : analyser des lignes de log nginx avec match.
#
# Rôle : extraire IP, méthode, chemin et code de chaque ligne, compter par classe.
# Lancé par : python3 solution/logs.py

LIGNES = [
    '203.0.113.7 - - [04/Sep/2026:10:00:01 +0200] "GET /index.html HTTP/1.1" 200 1043 "-" "Mozilla/5.0"',
    '203.0.113.7 - - [04/Sep/2026:10:00:01 +0200] "GET /style.css HTTP/1.1" 200 512 "-" "Mozilla/5.0"',
    '198.51.100.23 - - [04/Sep/2026:10:00:05 +0200] "POST /api/login HTTP/1.1" 401 87 "-" "curl/8.4.0"',
    '203.0.113.7 - - [04/Sep/2026:10:00:06 +0200] "GET /favicon.ico HTTP/1.1" 404 153 "-" "Mozilla/5.0"',
    'garbage line that does not parse',
    '198.51.100.23 - - [04/Sep/2026:10:00:09 +0200] "GET /api/users HTTP/1.1" 500 21 "-" "curl/8.4.0"',
]

# Affectation en chaîne : les trois noms pointent sur le même objet 0.
# Sans danger ici parce qu'un int est immuable (chapitre 10 pour le cas des listes).
nb_2xx = nb_4xx = nb_5xx = 0

for ligne in LIGNES:
    mots = ligne.split()          # coupe sur les blancs, quel que soit leur nombre

    match mots:
        # Motif de séquence : « au moins 9 éléments, et je capture le 1er,
        # le 6e, le 7e et le 9e ». Le _ ignore une position, le *_ absorbe
        # tout ce qui reste (taille, referer, user-agent), quel qu'en soit
        # le nombre. La ligne « garbage » n'a que 5 mots : elle ne colle pas.
        case [ip, _, _, _, _, methode, chemin, _, code, *_]:
            methode = methode[1:]         # '"GET' → 'GET' : on saute le guillemet
            code = int(code)              # '200' → 200, pour faire de l'arithmétique

            # <16 : aligné à gauche sur 16 colonnes ; sans ça, les colonnes
            # dansent selon la longueur de l'IP.
            print(f"{ip:<16} {methode:<7} {chemin:<30} {code}")

            # // 100 isole la centaine : 200 → 2, 404 → 4, 500 → 5.
            # Un match imbriqué ferait aussi l'affaire ; ici l'if est plus court.
            classe = code // 100
            if classe == 2:
                nb_2xx += 1
            elif classe == 4:
                nb_4xx += 1
            elif classe == 5:
                nb_5xx += 1
        case _:
            print("ligne ignorée :", ligne)

print(f"2xx : {nb_2xx}   4xx : {nb_4xx}   5xx : {nb_5xx}")
