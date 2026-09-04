# inventaire.py — Labo 04 : un inventaire de serveurs à trier, filtrer, regrouper.
# Chaque serveur est un dict ; l'inventaire est une liste de dicts, exactement
# ce que renvoie un fichier JSON ou une API (chapitres 7 et 14).

from collections import Counter, defaultdict

SERVEURS = [
    {"nom": "web1",   "role": "web",   "os": "debian", "ram": 16},
    {"nom": "web2",   "role": "web",   "os": "debian", "ram": 16},
    {"nom": "db1",    "role": "db",    "os": "rhel",   "ram": 64},
    {"nom": "db2",    "role": "db",    "os": "rhel",   "ram": 64},
    {"nom": "cache1", "role": "cache", "os": "alpine", "ram": 8},
    {"nom": "lb1",    "role": "lb",    "os": "debian", "ram": 4},
    {"nom": "web1",   "role": "web",   "os": "debian", "ram": 16},   # doublon !
    {"nom": "mon1",   "role": "mon",   "os": "rhel",   "ram": 32},
]

# 1. Les serveurs web, par nom : une compréhension avec un if.
# TODO : web = [...]
# print("Serveurs web :", [s["nom"] for s in web])

# 2. Tri par RAM décroissante puis par nom : sorted() avec key=lambda s: (...)
# TODO : par_ram = sorted(...)
# for s in par_ram:
#     print(f"  {s['nom']:<8} {s['ram']:>3} Go")

# 3. RAM totale : sum() sur une expression génératrice.
# TODO : total = sum(...)
# print(f"RAM totale : {total} Go")

# 4. Nombre de serveurs par OS : un Counter sur les valeurs "os".
# TODO : par_os = Counter(...)
# for os_, n in par_os.most_common():
#     print(f"  {os_:<8} {n}")

# 5. Regrouper les NOMS par OS : defaultdict(list), une ligne par serveur.
# TODO : noms_par_os = defaultdict(list) ; puis boucle et append
# for os_, noms in sorted(noms_par_os.items()):
#     print(f"  {os_:<8} {', '.join(noms)}")

# 6. Doublons : un set des noms déjà vus ; un nom qu'on revoit est un doublon.
# TODO : vus = set() ; doublons = set() ; boucle
# print("Doublons :", sorted(doublons))

# 7. Bonus : le même inventaire en CSV (chaîne en dur). Reconstruis la liste
#    de dicts à partir de la chaîne : splitlines(), puis split(",") par ligne,
#    zip() des en-têtes et des valeurs, dict(). N'oublie pas int() pour la RAM.
CSV = """nom,role,os,ram
web1,web,debian,16
db1,db,rhel,64
cache1,cache,alpine,8"""
# TODO : depuis_csv = [...]
# print(depuis_csv == SERVEURS[:1] + SERVEURS[2:3] + SERVEURS[4:5])   # doit afficher True
