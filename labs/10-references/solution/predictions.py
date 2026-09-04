# solution/predictions.py — Labo 10 : les dix expériences, avec les réponses et le POURQUOI.
#
# Rôle : même code que le squelette, mais chaque expérience est suivie de son
#        explication. Lance-le et lis les commentaires en parallèle.
# Lancé par : python3 solution/predictions.py

import copy
import ctypes
import dis
import sys
import timeit


def titre(n, texte):
    print(f"\n--- {n}. {texte}")


# ---------------------------------------------------------------------------
titre(1, "Deux étiquettes, un objet (10.1)")
a = [1, 2, 3]
b = a
b.append(4)
print("a =", a, "| a is b :", a is b)
# Réponse : a = [1, 2, 3, 4], a is b = True.
# `b = a` ne copie rien : c'est une deuxième étiquette sur la même liste.
# append modifie l'objet sur place, donc a le voit. En C : int *b = a.

# ---------------------------------------------------------------------------
titre(2, "Un entier passé à une fonction (10.3)")
def incremente(n):
    n += 1          # int immuable : crée un nouvel objet 11, l'étiquette LOCALE n bouge
    return n

x = 10
incremente(x)       # la valeur renvoyée est jetée
print("x =", x)
# Réponse : x = 10. La fonction a rebindé son propre paramètre, pas x.
# Pour « modifier » un int, il n'y a qu'une façon : x = incremente(x).

# ---------------------------------------------------------------------------
titre(3, "Une liste passée à une fonction (10.3)")
def ajoute(liste):
    liste.append("nouveau")      # mutation sur place → visible par l'appelant

def remplace(liste):
    liste = ["remplacé"]         # rebind du paramètre local → invisible

hosts = ["web-01"]
ajoute(hosts)
remplace(hosts)
print("hosts =", hosts)
# Réponse : ['web-01', 'nouveau']. Ni « par valeur » ni « par référence » :
# le paramètre est une étiquette sur le même objet. Muter = partagé ;
# affecter = local. C'est la règle qui résume tout le chapitre.

# ---------------------------------------------------------------------------
titre(4, "+= sur une liste, += sur un tuple (10.3)")
l = [1, 2]; l2 = l
l += [3]            # list a __iadd__ : extend sur place, même objet
t = (1, 2); t2 = t
t += (3,)           # tuple n'a pas __iadd__ : t = t + (3,), nouvel objet
print("l is l2 :", l is l2, "| t is t2 :", t is t2)
# Réponse : True, False. Le même opérateur fait deux choses différentes selon
# que le type sait se modifier sur place. Sur une liste, += est un extend
# (et l2 le voit) ; sur un tuple, c'est une concaténation + réaffectation.

# ---------------------------------------------------------------------------
titre(5, "[x] * n (10.4)")
grille = [[0, 0]] * 3            # TROIS étiquettes sur UNE liste [0, 0]
grille[0][0] = 7
print("grille =", grille)
# Réponse : [[7, 0], [7, 0], [7, 0]]. La multiplication répète la référence,
# pas l'objet. Pour trois lignes indépendantes : [[0, 0] for _ in range(3)],
# où l'expression [0, 0] est évaluée à chaque tour.

# ---------------------------------------------------------------------------
titre(6, "Copie superficielle vs profonde (10.4)")
orig = {"web": ["01", "02"], "db": ["01"]}
sup = dict(orig)             # nouveau dict, mais les VALEURS sont les mêmes listes
prof = copy.deepcopy(orig)   # tout est dupliqué, récursivement
orig["web"].append("03")     # mute une liste partagée avec sup
orig["cache"] = ["01"]       # ajoute une clé à orig seulement
print("sup  =", sup)
print("prof =", prof)
# Réponse : sup = {'web': ['01', '02', '03'], 'db': ['01']}  (voit le append, pas la clé)
#           prof = {'web': ['01', '02'], 'db': ['01']}        (ne voit rien)
# La copie superficielle protège le conteneur, pas son contenu.

# ---------------------------------------------------------------------------
titre(7, "Défaut mutable (10.3, rappel du chapitre 5)")
def collecte(valeur, panier=[]):    # [] évalué UNE fois, à la définition
    panier.append(valeur)
    return panier

p1 = collecte(1)
p2 = collecte(2)
print("p1 =", p1, "| p1 is p2 :", p1 is p2)
# Réponse : p1 = [1, 2], p1 is p2 = True. Le défaut est un seul objet stocké
# dans collecte.__defaults__, partagé par tous les appels. Idiome correct :
#   def collecte(valeur, panier=None):
#       if panier is None: panier = []

# ---------------------------------------------------------------------------
titre(8, "Compteur de références (10.5)")
donnees = [1, 2, 3]
alias = donnees
conteneur = {"d": donnees}
print("refcount :", sys.getrefcount(donnees))
del alias
print("après del alias :", sys.getrefcount(donnees))
# Réponse : 4 puis 3. Les étiquettes : donnees, alias, la valeur du dict, et
# l'argument temporaire passé à getrefcount lui-même (+1 le temps de l'appel).
# del alias retire une étiquette, pas l'objet : il reste deux vraies références.

# ---------------------------------------------------------------------------
titre(9, "Bytecode (10.6)")
def moyenne(valeurs):
    return sum(valeurs) / len(valeurs)

dis.dis(moyenne)
# Lecture (3.13 ; la forme exacte varie selon la version) :
#   LOAD_GLOBAL  sum      ← sum n'est pas locale : cherchée dans les globales, puis les builtins
#   LOAD_FAST    valeurs  ← variable locale (un slot indexé, d'où FAST)
#   CALL         1        ← appel avec 1 argument
#   LOAD_GLOBAL  len / LOAD_FAST valeurs / CALL 1
#   BINARY_OP    /        ← dépile deux valeurs, divise, rempile
#   RETURN_VALUE
# Chaque LOAD_GLOBAL est une recherche de dictionnaire à l'exécution : c'est
# pour ça que, dans une boucle très chaude, on voit parfois `s = sum` en local.

# ---------------------------------------------------------------------------
titre(10, "Mesurer (10.8)")
N = 200_000
def boucle():
    total = 0
    for i in range(N):
        total += i          # ~6 instructions de bytecode par tour, avec dispatch dynamique
    return total

def builtin():
    return sum(range(N))    # la boucle est dans sum, en C

def compr():
    return sum([i for i in range(N)])   # construit une liste de 200 000 objets, puis somme

for f in (boucle, builtin, compr):
    ms = timeit.timeit(f, number=20) / 20 * 1000
    print(f"{f.__name__:8s} {ms:6.2f} ms")
# Réponse (ordre de grandeur, dépend de la machine) : builtin ~2× plus rapide
# que boucle ; compr ≈ boucle, parce qu'elle paie l'allocation de la liste
# intermédiaire. sum(i for i in range(N)) sans crochets éviterait la liste
# mais garde la boucle en bytecode. Le gagnant est celui qui ne fait PAS
# tourner de bytecode par élément.

# ---------------------------------------------------------------------------
titre(11, "ctypes : strlen de la libc (10.8)")
libc = ctypes.CDLL(None)                   # None = le processus courant, où la libc est déjà chargée
libc.strlen.argtypes = [ctypes.c_char_p]   # char * : il faut des bytes, pas un str
libc.strlen.restype = ctypes.c_size_t
print("strlen(b'stranix') =", libc.strlen(b"stranix"))
try:
    libc.strlen("stranix")                 # str : ctypes refuse grâce à argtypes
except ctypes.ArgumentError as e:
    print("avec un str :", type(e).__name__, "-", str(e).splitlines()[0])
# Sans argtypes, ctypes accepterait le str et le passerait comme wchar_t*
# (UTF-16/32) : strlen s'arrêterait au premier octet nul, donc après 1 caractère.
# Déclarer le prototype, c'est exactement ce que fait un .h en C.

# ---------------------------------------------------------------------------
# 12. Voir gil_demo.py (et son commentaire d'en-tête).
