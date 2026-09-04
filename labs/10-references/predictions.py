# predictions.py — Labo 10 : dix expériences sur le modèle mémoire de Python.
#
# Règle du jeu : pour CHAQUE expérience, écris ta prédiction dans le
# commentaire « Prédiction : » AVANT de lancer. Puis lance, compare, et si tu
# t'es trompé, relis la section du chapitre 10 indiquée. Le but n'est pas
# d'avoir bon, c'est de savoir POURQUOI la réponse est celle-là.
#
# Lance : python3 predictions.py

import copy
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
# Prédiction : a = ?          a is b = ?
print("a =", a, "| a is b :", a is b)

# ---------------------------------------------------------------------------
titre(2, "Un entier passé à une fonction (10.3)")
def incremente(n):
    n += 1
    return n

x = 10
incremente(x)
# Prédiction : x = ?
print("x =", x)

# ---------------------------------------------------------------------------
titre(3, "Une liste passée à une fonction (10.3)")
def ajoute(liste):
    liste.append("nouveau")

def remplace(liste):
    liste = ["remplacé"]

hosts = ["web-01"]
ajoute(hosts)
remplace(hosts)
# Prédiction : hosts = ?
print("hosts =", hosts)

# ---------------------------------------------------------------------------
titre(4, "+= sur une liste, += sur un tuple (10.3)")
l = [1, 2]; l2 = l
l += [3]
t = (1, 2); t2 = t
t += (3,)
# Prédiction : l is l2 = ?    t is t2 = ?
print("l is l2 :", l is l2, "| t is t2 :", t is t2)

# ---------------------------------------------------------------------------
titre(5, "[x] * n (10.4)")
grille = [[0, 0]] * 3
grille[0][0] = 7
# Prédiction : grille = ?
print("grille =", grille)

# ---------------------------------------------------------------------------
titre(6, "Copie superficielle vs profonde (10.4)")
orig = {"web": ["01", "02"], "db": ["01"]}
sup = dict(orig)             # ou orig.copy()
prof = copy.deepcopy(orig)
orig["web"].append("03")
orig["cache"] = ["01"]
# Prédiction : sup = ?        prof = ?
print("sup  =", sup)
print("prof =", prof)

# ---------------------------------------------------------------------------
titre(7, "Défaut mutable (10.3, rappel du chapitre 5)")
def collecte(valeur, panier=[]):
    panier.append(valeur)
    return panier

p1 = collecte(1)
p2 = collecte(2)
# Prédiction : p1 = ?         p1 is p2 = ?
print("p1 =", p1, "| p1 is p2 :", p1 is p2)

# ---------------------------------------------------------------------------
titre(8, "Compteur de références (10.5)")
donnees = [1, 2, 3]
alias = donnees
conteneur = {"d": donnees}
# Prédiction : getrefcount = ?  (compte les étiquettes, sans oublier l'argument)
print("refcount :", sys.getrefcount(donnees))
del alias
print("après del alias :", sys.getrefcount(donnees))

# ---------------------------------------------------------------------------
titre(9, "Bytecode (10.6)")
def moyenne(valeurs):
    return sum(valeurs) / len(valeurs)

# Prédiction : combien d'instructions (lignes de bytecode) pour cette fonction ?
#              Quelles instructions apparaissent ? (LOAD_GLOBAL ? LOAD_FAST ? CALL ?)
dis.dis(moyenne)

# ---------------------------------------------------------------------------
titre(10, "Mesurer (10.8)")
N = 200_000
def boucle():
    total = 0
    for i in range(N):
        total += i
    return total

def builtin():
    return sum(range(N))

def compr():
    return sum([i for i in range(N)])

# Prédiction : classe les trois du plus rapide au plus lent, et estime le rapport.
for f in (boucle, builtin, compr):
    ms = timeit.timeit(f, number=20) / 20 * 1000
    print(f"{f.__name__:8s} {ms:6.2f} ms")

# ---------------------------------------------------------------------------
# TODO (bonus) : 11. Appelle strlen de la libc via ctypes sur b"stranix".
#   Indices : ctypes.CDLL(None), .argtypes = [ctypes.c_char_p], .restype = ctypes.c_size_t.
#   Puis essaie SANS déclarer argtypes/restype avec une chaîne str : que se passe-t-il ?

# TODO (bonus) : 12. Lance gil_demo.py et explique les trois temps.
