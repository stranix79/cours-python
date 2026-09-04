# 11. Itérateurs, générateurs, décorateurs, `with`

*Python de zéro à FastAPI — chapitre 11 sur 21.* ← [10. Sous le capot : références, mémoire, GIL, bytecode](10-sous-le-capot.md) · [Sommaire](../README.md) · [12. Tester avec pytest](12-tests-pytest.md) →

> 🧪 Labo associé : [`labs/11-pipeline-logs`](../labs/11-pipeline-logs/README.md)

Ce chapitre regroupe quatre mécanismes que tu croises dans *toutes* les bibliothèques Python sans forcément les avoir écrits toi-même : le protocole d'itération, les générateurs, les décorateurs et les gestionnaires de contexte. Ils ont un point commun : chacun est du sucre syntaxique sur une idée simple, et une fois l'idée vue, le sucre devient évident. FastAPI, pytest, SQLAlchemy et `open()` reposent dessus.

### 11.1 Ce que fait vraiment `for`

En C, `for` c'est un compteur. En Python, `for` ne connaît pas les compteurs : il connaît les **itérables**. Une liste, une chaîne, un fichier, un dict, un `range`, une réponse HTTP en streaming… tout ce sur quoi on peut appeler `iter()`.

```python
>>> liste = [10, 20, 30]
>>> it = iter(liste)          # demande un itérateur à la liste
>>> next(it)
10
>>> next(it)
20
>>> next(it)
30
>>> next(it)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

C'est tout le protocole. Quand tu écris `for x in liste:`, Python fait exactement ça : `it = iter(liste)`, puis `next(it)` en boucle jusqu'à attraper `StopIteration`. Deux méthodes spéciales derrière : `__iter__()` (rend un itérateur) et `__next__()` (rend l'élément suivant, ou lève `StopIteration`).

Un **itérable** est un objet qui a `__iter__`. Un **itérateur** est un objet qui a `__next__` (et `__iter__` qui rend `self`, pour pouvoir être utilisé dans un `for`). La liste est itérable mais pas itérateur : on peut la parcourir plusieurs fois, chaque `iter()` repart du début. L'itérateur, lui, est **consommable** : une fois épuisé, il est vide.

> **Piège** : un itérateur ne se rembobine pas. `lignes = iter(fichier)` puis deux `for` dessus : le second ne verra rien. Idem pour `zip()`, `map()`, `filter()`, `enumerate()`, `reversed()`, un fichier ouvert : tous rendent des itérateurs à usage unique. Si tu as besoin de passer deux fois, `list()` d'abord.

Écrire son propre itérateur en classe, pour voir la mécanique :

```python
class Compteur:
    """Compte de 1 à fin, comme range(1, fin + 1), mais à la main."""

    def __init__(self, fin):
        self.i = 0
        self.fin = fin

    def __iter__(self):
        return self              # je suis mon propre itérateur

    def __next__(self):
        if self.i >= self.fin:
            raise StopIteration  # le signal de fin, pas une erreur
        self.i += 1
        return self.i
```

```python
>>> list(Compteur(3))
[1, 2, 3]
```

Trois méthodes et un état à maintenir soi-même. Ça marche, c'est verbeux, et personne ne l'écrit comme ça. On écrit un générateur.

### 11.2 Générateurs : `yield`

```python
def compteur(fin):
    i = 0
    while i < fin:
        i += 1
        yield i          # « rends cette valeur, et mets-moi en pause ici »
```

```python
>>> g = compteur(3)
>>> g
<generator object compteur at 0x104131a80>
>>> next(g)
1
>>> next(g)
2
>>> next(g)
3
>>> next(g)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

Dès qu'une fonction contient `yield`, appeler la fonction **n'exécute pas son corps** : ça rend un objet générateur, qui est un itérateur. Chaque `next()` fait tourner le corps jusqu'au prochain `yield`, rend la valeur, et **gèle la fonction** : ses variables locales, sa position, tout. Le `next()` suivant reprend juste après le `yield`. Quand la fonction se termine (ou fait `return`), `StopIteration`.

> **Venant du C** : c'est une fonction avec un pointeur d'instruction et une pile sauvegardés entre deux appels. En C, tu simulerais ça avec une `static` et un `switch` (le « Duff's device » des coroutines de Simon Tatham). Python le fait pour toi, et c'est le mécanisme qui, sous une autre syntaxe, donne `async`/`await` au chapitre 15.

L'intérêt n'est pas d'économiser trois lignes. C'est la **paresse** (*laziness*) : rien n'est calculé avant qu'on le demande, et une seule valeur existe en mémoire à la fois.

```python
def lignes(chemin):
    with open(chemin) as f:
        for ligne in f:
            yield ligne.rstrip("\n")
```

Ce générateur lit un fichier de 40 Go ligne par ligne sans jamais en charger plus d'une. Et il marche aussi avec un flux qui ne finit jamais :

```python
import itertools

def naturels():
    n = 0
    while True:          # infini, et ce n'est pas un problème
        yield n
        n += 1
```

```python
>>> list(itertools.islice(naturels(), 5))
[0, 1, 2, 3, 4]
```

Tant que personne n'appelle `next()`, l'infini ne coûte rien.

**Expression génératrice.** Une compréhension avec des parenthèses au lieu de crochets :

```python
>>> import sys
>>> carres_liste = [x * x for x in range(1_000_000)]
>>> carres_gen = (x * x for x in range(1_000_000))
>>> sys.getsizeof(carres_liste), sys.getsizeof(carres_gen)
(8448728, 200)
```

Huit mégaoctets contre deux cents octets. La liste a tout calculé et tout stocké ; le générateur n'a rien fait encore. Règle : si tu ne fais que **parcourir une fois** (`sum`, `max`, `for`, `join`, `any`), utilise un générateur. Si tu as besoin d'indexer, de mesurer la longueur ou de repasser, une liste.

```python
total = sum(x * x for x in range(1_000_000))   # pas de crochets : rien n'est stocké
```

**`yield from`** délègue à un autre itérable, pratique pour composer ou pour parcourir récursivement :

```python
def gen_a():
    yield 1
    yield 2

def gen_b():
    yield from gen_a()    # équivaut à : for x in gen_a(): yield x
    yield 3
```

```python
>>> list(gen_b())
[1, 2, 3]
```

### 11.3 `itertools` et `functools` : la boîte à outils

Deux modules de la bibliothèque standard à connaître par leur table des matières.

| `itertools` | Ce que ça fait |
|---|---|
| `count(start, step)` | compteur infini |
| `islice(it, n)` / `islice(it, a, b)` | les n premiers, ou une tranche, **sans liste intermédiaire** |
| `chain(a, b, …)` | enchaîne plusieurs itérables |
| `takewhile(pred, it)` / `dropwhile` | prend tant que / saute tant que |
| `groupby(it, key)` | regroupe les éléments **consécutifs** égaux (trie avant, comme `sort \| uniq -c`) |
| `batched(it, n)` | paquets de n (3.12+) |
| `product`, `permutations`, `combinations` | combinatoire |
| `pairwise(it)` | couples `(a, b), (b, c), …` |

```python
>>> import itertools as it
>>> list(it.islice(it.count(1), 5))
[1, 2, 3, 4, 5]
>>> list(it.chain([1, 2], (3, 4)))
[1, 2, 3, 4]
>>> list(it.takewhile(lambda x: x < 4, it.count(1)))
[1, 2, 3]
>>> for cle, grp in it.groupby("aabbbc"):
...     print(cle, len(list(grp)))
a 2
b 3
c 1
>>> list(it.batched(range(7), 3))
[(0, 1, 2), (3, 4, 5), (6,)]
```

| `functools` | Ce que ça fait |
|---|---|
| `partial(f, *args, **kw)` | fixe des arguments : une nouvelle fonction avec moins de paramètres |
| `reduce(f, it)` | replie : `f(f(f(a, b), c), d)` |
| `lru_cache` / `cache` | mémoïse une fonction : mêmes arguments, résultat mis en cache |
| `wraps` | pour les décorateurs, voir 11.5 |
| `cached_property` | une `@property` calculée une fois |

```python
>>> import functools
>>> functools.reduce(lambda a, b: a * b, [1, 2, 3, 4])
24
>>> hexa = functools.partial(int, base=16)
>>> hexa("ff")
255
>>> @functools.lru_cache(maxsize=None)
... def fib(n):
...     return n if n < 2 else fib(n - 1) + fib(n - 2)
...
>>> fib(80), fib.cache_info()
(23416728348467685, CacheInfo(hits=78, misses=81, maxsize=None, currsize=81))
```

Sans le cache, `fib(80)` ferait des milliards d'appels. Avec, 81. Le cache est un dict `arguments → résultat` accroché à la fonction, rien de plus. Condition : les arguments doivent être hachables (chapitre 4) et la fonction pure.

### 11.4 Un générateur, c'est un tube Unix

Un DevOps pense en `cat access.log | grep " 500 " | cut -d' ' -f1 | sort | uniq -c`. Un générateur, c'est exactement un maillon de ce tube : il consomme un flux, produit un flux, ne stocke rien.

```python
from collections import Counter

def grep(motif, lignes):
    for ligne in lignes:
        if motif in ligne:
            yield ligne

def cut(champ, lignes):
    for ligne in lignes:
        yield ligne.split()[champ]

lignes = ["GET /index 200", "GET /admin 403", "POST /api 500", "GET /x 200"]
```

```python
>>> sorted(cut(2, grep("GET", lignes)))
['200', '200', '403']
>>> Counter(cut(2, lignes)).most_common(2)
[('200', 2), ('403', 1)]
```

Chaque étage tire sur le précédent une ligne à la fois. Sur un fichier d'un milliard de lignes, la mémoire reste plate. C'est le cœur du labo 11.

### 11.5 Décorateurs

**Étape 1 : une fonction peut fabriquer une fonction.** Tu l'as vu au chapitre 5 avec les closures :

```python
def fabrique_multiplicateur(k):
    def multiplie(x):
        return x * k          # k vient de la fonction englobante, capturé
    return multiplie
```

```python
>>> double = fabrique_multiplicateur(2)
>>> double(21)
42
```

**Étape 2 : une fonction peut prendre une fonction et en rendre une autre** qui fait la même chose, plus quelque chose autour. C'est ça, un décorateur. Rien d'autre.

```python
import functools
import time

def chrono(fonction):
    @functools.wraps(fonction)             # explication juste après
    def enveloppe(*args, **kwargs):        # accepte n'importe quels arguments
        debut = time.perf_counter()
        resultat = fonction(*args, **kwargs)   # appelle l'originale
        duree = time.perf_counter() - debut
        print(f"{fonction.__name__} : {duree * 1000:.1f} ms")
        return resultat                    # sans ça, l'appelant reçoit None
    return enveloppe
```

**Étape 3 : la syntaxe `@`.** Ces deux écritures sont strictement équivalentes :

```python
def lent():
    time.sleep(0.05)
    return 42
lent = chrono(lent)          # on remplace le nom par la version enveloppée

@chrono                      # la même chose, écrite au-dessus de la définition
def lent():
    time.sleep(0.05)
    return 42
```

```python
>>> lent()
lent : 50.6 ms
42
```

`@truc` au-dessus d'un `def f` veut dire `f = truc(f)`. C'est de la réaffectation de variable, et rien de plus. Ce qui explique que tu peux décorer avec n'importe quel appelable, empiler plusieurs décorateurs (ils s'appliquent de bas en haut), et décorer des méthodes ou des classes.

**`@functools.wraps`.** Sans lui, `lent.__name__` vaudrait `"enveloppe"` et la docstring serait perdue : l'enveloppe a masqué l'originale. `wraps` recopie nom, doc, signature, module. Toujours le mettre : les outils (pytest, FastAPI, la doc auto) lisent ces attributs.

**Décorateur avec paramètres.** `@retry(essais=3)` : ici `retry(essais=3)` est *appelé d'abord*, et doit rendre un décorateur. Trois niveaux de fonctions, c'est le prix.

```python
def retry(essais=3, delai=0.0):
    def decorateur(fonction):
        @functools.wraps(fonction)
        def enveloppe(*args, **kwargs):
            for tentative in range(1, essais + 1):
                try:
                    return fonction(*args, **kwargs)
                except Exception as err:
                    if tentative == essais:
                        raise                      # dernière chance : on propage
                    print(f"{fonction.__name__} a échoué ({err}), "
                          f"tentative {tentative}/{essais}")
                    time.sleep(delai)
        return enveloppe
    return decorateur
```

```python
>>> appels = {"n": 0}
>>> @retry(essais=3)
... def flaky():
...     appels["n"] += 1
...     if appels["n"] < 3:
...         raise ConnectionError("timeout")
...     return "ok"
...
>>> flaky()
flaky a échoué (timeout), tentative 1/3
flaky a échoué (timeout), tentative 2/3
'ok'
```

Voilà un `retry` réutilisable sur n'importe quel appel SSH, HTTP ou base de données, sans toucher au code de la fonction. C'est ce que les décorateurs achètent : de la **séparation** entre ce que fait la fonction et ce qui l'entoure (mesure, cache, journalisation, nouvelle tentative, contrôle d'accès, enregistrement dans une table de routes).

> **Venant de Java** : c'est ce que font les annotations `@Transactional` ou `@GetMapping` de Spring, mais en Java l'annotation est inerte et c'est le framework qui la lit par réflexion. En Python, le décorateur *est* du code qui s'exécute à la définition. Pas de magie cachée : tu peux lire `retry` ligne par ligne.

**Ceux que tu vas croiser sans les écrire.**

- `@property` (chapitre 9) : transforme une méthode en attribut calculé. Un décorateur, écrit en C, qui rend un objet *descripteur*.
- `@dataclass` (chapitre 9) : prend une **classe**, lit ses annotations, et lui *ajoute* `__init__`, `__repr__`, `__eq__`. Un décorateur de classe.
- `@lru_cache` : vu plus haut.
- `@pytest.fixture` (chapitre 12) : enregistre une fonction dans le registre des fixtures.
- `@app.get("/items")` (chapitre 17) : `app.get("/items")` rend un décorateur qui **enregistre** ta fonction dans la table de routage de FastAPI, puis la rend inchangée. Quand tu liras `@app.get`, tu sauras que c'est `retry` avec une table à la place d'une boucle.

### 11.6 Gestionnaires de contexte : `with`

Tu connais déjà le `with` sur les fichiers :

```python
with open("config.yaml") as f:
    contenu = f.read()
# ici, f est fermé, même si read() a levé une exception
```

Le mécanisme : `with X as y:` appelle `X.__enter__()` (dont le résultat va dans `y`), exécute le bloc, puis appelle `X.__exit__(type, valeur, traceback)` **quoi qu'il arrive** : sortie normale, `return`, `break`, exception. C'est le `try / finally` du chapitre 8 emballé dans l'objet lui-même, pour que l'appelant ne puisse pas oublier de libérer.

```python
class Fichier:
    def __init__(self, chemin):
        self.chemin = chemin

    def __enter__(self):
        print("ouverture")
        return self                 # ce que reçoit le « as »

    def __exit__(self, exc_type, exc, tb):
        print("fermeture", exc_type)
        return False                # False : ne pas avaler l'exception éventuelle
```

```python
>>> with Fichier("x") as f:
...     print("dedans", f.chemin)
...
ouverture
dedans x
fermeture None
```

Si le bloc lève, `__exit__` reçoit le type de l'exception dans `exc_type` ; rendre `True` la supprime, `False` la laisse remonter. Ne rends `True` que si tu sais ce que tu fais.

> **Venant du C** : c'est le RAII de C++ (destructeur à la sortie du bloc), ou le `defer` de Go, ou le `try-with-resources` de Java 7. Le point commun : la libération est attachée au bloc, pas à la bonne volonté du programmeur. En C pur, c'est `goto cleanup;`, et on connaît la suite.

**Avec un générateur.** Écrire une classe pour deux méthodes est lourd. `contextlib.contextmanager` transforme un générateur en gestionnaire de contexte : tout ce qui est avant `yield` est le `__enter__`, tout ce qui est après est le `__exit__`.

```python
import os
import time
from contextlib import contextmanager

@contextmanager
def chronometre(nom):
    debut = time.perf_counter()
    try:
        yield                       # ici s'exécute le bloc du with
    finally:                        # finally : même si le bloc a levé
        print(f"{nom} : {(time.perf_counter() - debut) * 1000:.1f} ms")

@contextmanager
def dans_dossier(chemin):
    avant = os.getcwd()
    os.chdir(chemin)
    try:
        yield
    finally:
        os.chdir(avant)             # on revient toujours au dossier de départ
```

```python
>>> with chronometre("boucle"):
...     sum(range(1_000_000))
...
boucle : 14.4 ms
>>> with dans_dossier("/tmp"):
...     print(os.getcwd())
...
/private/tmp
```

Le `try / finally` autour du `yield` est indispensable : sans lui, une exception dans le bloc sauterait la partie « après ». Un `yield` unique par générateur, sinon `RuntimeError`.

Où on en trouve : `open()`, `threading.Lock()` (`with verrou:`), `socket`, les connexions et transactions de base de données (chapitre 18 : `with Session(engine) as session:`), `tempfile.TemporaryDirectory()`, `contextlib.suppress(FileNotFoundError)` pour ignorer une exception précise, `pytest.raises` (chapitre 12), les clients HTTP (`with httpx.Client() as client:`, chapitre 14). Dès que tu écris « ouvrir… fermer », « acquérir… relâcher », « commencer… terminer », c'est un gestionnaire de contexte.

### 11.7 Ce qu'il faut retenir

- `for` = `iter()` puis `next()` jusqu'à `StopIteration`. Un itérateur est à usage unique.
- `yield` transforme une fonction en générateur : paresseux, une valeur à la fois, sait gérer l'infini. `(x for x in …)` pour parcourir une fois, `[x for x in …]` pour stocker.
- Un générateur par étage = un tube Unix en Python. `itertools` et `functools` sont les `coreutils` de ce monde.
- `@deco` au-dessus de `def f` signifie `f = deco(f)`. Un décorateur est une fonction qui reçoit une fonction et rend une fonction. Toujours `@functools.wraps`.
- `with` appelle `__enter__` / `__exit__` ; `@contextmanager` l'écrit en trois lignes autour d'un `yield`. Tout ce qui s'ouvre et se ferme passe par là.

**Labo 11** : un pipeline d'analyse de logs nginx avec des générateurs, un décorateur `@chrono`, un gestionnaire de contexte, et un `tail -f` en générateur infini.

---

← [10. Sous le capot : références, mémoire, GIL, bytecode](10-sous-le-capot.md) · [Sommaire](../README.md) · [12. Tester avec pytest](12-tests-pytest.md) →
