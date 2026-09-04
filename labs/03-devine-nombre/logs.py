# logs.py — Labo 03 (bonus) : analyser des lignes de log nginx avec match.

# Format « combined » de nginx, un espace entre chaque champ.
# Après split(), une ligne normale donne 12 mots :
#   [ip, '-', user, '[date', 'fuseau]', '"GET', '/chemin', 'HTTP/1.1"', code, taille, '"referer"', '"agent"']
LIGNES = [
    '203.0.113.7 - - [04/Sep/2026:10:00:01 +0200] "GET /index.html HTTP/1.1" 200 1043 "-" "Mozilla/5.0"',
    '203.0.113.7 - - [04/Sep/2026:10:00:01 +0200] "GET /style.css HTTP/1.1" 200 512 "-" "Mozilla/5.0"',
    '198.51.100.23 - - [04/Sep/2026:10:00:05 +0200] "POST /api/login HTTP/1.1" 401 87 "-" "curl/8.4.0"',
    '203.0.113.7 - - [04/Sep/2026:10:00:06 +0200] "GET /favicon.ico HTTP/1.1" 404 153 "-" "Mozilla/5.0"',
    'garbage line that does not parse',
    '198.51.100.23 - - [04/Sep/2026:10:00:09 +0200] "GET /api/users HTTP/1.1" 500 21 "-" "curl/8.4.0"',
]

nb_2xx = nb_4xx = nb_5xx = 0

for ligne in LIGNES:
    mots = ligne.split()
    # TODO : match mots:
    #   case [ip, _, _, _, _, methode, chemin, _, code, *_]:
    #       - methode commence par un guillemet : methode[1:] l'enlève
    #       - code est une str : int(code) pour compter
    #       - afficher f"{ip:<16} {methode:<7} {chemin:<30} {code}"
    #       - compter selon la centaine : code // 100 == 2, 4 ou 5
    #   case _:
    #       print("ligne ignorée :", ligne)
    pass

print(f"2xx : {nb_2xx}   4xx : {nb_4xx}   5xx : {nb_5xx}")
