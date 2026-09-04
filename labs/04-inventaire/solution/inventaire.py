# solution/inventaire.py — Labo 04 : un inventaire de serveurs, version commentée.
#
# Rôle : filtrer, trier, regrouper, sommer et dédoublonner une liste de dicts.
# Lancé par : python3 solution/inventaire.py
#
# Le point de ce labo : une liste de dicts est LA forme des données qu'on
# manipule tout le temps (JSON d'une API, lignes d'un CSV, inventaire Ansible),
# et chaque question qu'on lui pose correspond à une structure précise.

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

# --- 1. Filtrer : une compréhension avec un if -------------------------------
# Se lit « les s de SERVEURS dont le rôle est web ». Équivalent SQL :
# SELECT * FROM serveurs WHERE role = 'web'.
web = [s for s in SERVEURS if s["role"] == "web"]
print("Serveurs web :", [s["nom"] for s in web])

# --- 2. Trier : sorted() renvoie une nouvelle liste, SERVEURS est intact ----
# La clé renvoie un tuple : Python compare d'abord -ram (négatif pour avoir
# le plus gros en premier), puis le nom en cas d'égalité. C'est le
# ORDER BY ram DESC, nom de SQL. Le tri est stable, mais ici on n'en a même
# pas besoin puisque le nom départage.
par_ram = sorted(SERVEURS, key=lambda s: (-s["ram"], s["nom"]))
print("Par RAM décroissante :")
for s in par_ram:
    print(f"  {s['nom']:<8} {s['ram']:>3} Go")

# --- 3. Sommer : sum() sur une expression génératrice ------------------------
# Pas de crochets : on ne construit pas de liste intermédiaire, sum() consomme
# les valeurs une par une (chapitre 11). Sur 8 éléments ça ne change rien ;
# sur 8 millions, si.
total = sum(s["ram"] for s in SERVEURS)
print(f"RAM totale : {total} Go")

# --- 4. Compter : Counter ----------------------------------------------------
# Counter reçoit un itérable et compte chaque valeur. most_common() sans
# argument renvoie tout, du plus fréquent au moins fréquent.
par_os = Counter(s["os"] for s in SERVEURS)
print("Serveurs par OS :")
for os_, n in par_os.most_common():          # os_ : os est un module de la stdlib
    print(f"  {os_:<8} {n}")

# --- 5. Regrouper : defaultdict(list) ----------------------------------------
# À la première rencontre d'un OS, defaultdict appelle list() pour créer la
# valeur ; on peut donc faire append directement. Sans lui :
#   if s["os"] not in noms_par_os: noms_par_os[s["os"]] = []
noms_par_os = defaultdict(list)
for s in SERVEURS:
    noms_par_os[s["os"]].append(s["nom"])
print("Noms par OS :")
for os_, noms in sorted(noms_par_os.items()):  # sorted sur les couples : par clé
    print(f"  {os_:<8} {', '.join(noms)}")

# --- 6. Dédoublonner : un set --------------------------------------------------
# `nom in vus` est en O(1) grâce au hachage. Avec une liste, ce serait O(n)
# à chaque tour, soit O(n²) au total : invisible sur 8 serveurs, catastrophique
# sur 100 000 lignes de log.
vus: set[str] = set()
doublons: set[str] = set()
for s in SERVEURS:
    if s["nom"] in vus:
        doublons.add(s["nom"])
    vus.add(s["nom"])
print("Doublons :", sorted(doublons))

# Variante en une ligne avec Counter, pour comparer :
#   doublons = {nom for nom, n in Counter(s["nom"] for s in SERVEURS).items() if n > 1}

# --- 7. Bonus : reconstruire la liste de dicts depuis du CSV -----------------
CSV = """nom,role,os,ram
web1,web,debian,16
db1,db,rhel,64
cache1,cache,alpine,8"""

lignes = CSV.splitlines()             # coupe sur les fins de ligne → liste de str
entetes = lignes[0].split(",")        # ['nom', 'role', 'os', 'ram']

depuis_csv = []
for ligne in lignes[1:]:              # toutes les lignes sauf l'en-tête
    valeurs = ligne.split(",")
    # zip() apparie en-têtes et valeurs deux à deux ; dict() en fait un dict.
    # C'est exactement ce que fait csv.DictReader (chapitre 7).
    s = dict(zip(entetes, valeurs))
    s["ram"] = int(s["ram"])          # tout ce qui sort d'un CSV est une str
    depuis_csv.append(s)

# == compare le CONTENU des listes et des dicts, pas leur identité.
print("CSV == inventaire :", depuis_csv == SERVEURS[:1] + SERVEURS[2:3] + SERVEURS[4:5])
