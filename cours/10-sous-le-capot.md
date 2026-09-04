# 10. Sous le capot : références, mémoire, GIL, bytecode

*Python de zéro à FastAPI — chapitre 10 sur 21.* ← [9. Classes et objets](09-classes-et-objets.md) · [Sommaire](../README.md) · [11. Itérateurs, générateurs, décorateurs, `with`](11-iterateurs-generateurs-decorateurs.md) →

> 🧪 Labo associé : [`labs/10-references`](../labs/10-references/README.md)

Tu sais écrire du Python. Ce chapitre explique ce qui se passe quand il tourne, parce que c'est là que se cachent les surprises de ceux qui viennent du C : une liste modifiée « à distance », une copie qui n'en est pas une, deux threads qui ne vont pas plus vite qu'un seul. Rien de tout ça n'est un bug. C'est le modèle mémoire de Python, et il tient en une page.

### 10.1 Tout est objet, une variable est une étiquette

En C, `int a = 5;` réserve quatre octets sur la pile et y écrit 5. La variable *est* la case.

En Python, `a = 5` fait deux choses : créer (ou retrouver) un **objet** entier de valeur 5 quelque part sur le tas, et lier le **nom** `a` à cet objet. La variable n'est pas une case, c'est une étiquette collée sur un objet. Un objet CPython, en mémoire, c'est une struct C qui commence toujours pareil :

```c
typedef struct {
    Py_ssize_t ob_refcnt;      /* combien d'étiquettes pointent ici */
    PyTypeObject *ob_type;     /* pointeur vers le type (int, str, list...) */
    /* ... puis les données propres au type */
} PyObject;
```

D'où `sys.getsizeof(0)` qui vaut 28 octets et pas 4 : compteur de références, pointeur de type, puis les chiffres. C'est le prix du « tout est objet ».

```python
>>> a = 5
>>> b = a          # b est une deuxième étiquette sur LE MÊME objet
>>> a is b
True
>>> a = a + 1      # crée un nouvel objet 6, déplace l'étiquette a dessus
>>> a, b, a is b
(6, 5, False)
```

```
   a = 5        b = a          a = a + 1

   a ──► [5]    a ──► [5]      a ──► [6]
                b ──┘          b ──► [5]
```

`is` compare les identités (« même objet ? », c'est une comparaison de pointeurs), `==` compare les valeurs (via `__eq__`). `id(x)` donne l'adresse de l'objet en CPython. Tu n'utilises `is` que pour `None`, `True`, `False` et les membres d'`Enum`.

**Curiosité** : CPython pré-alloue les entiers de -5 à 256 et internalise les chaînes courtes qui ressemblent à des identifiants. Donc dans le REPL `x = 100; y = 100; x is y` donne `True`, et avec 257 donne `False`. Ne t'appuie jamais dessus : c'est un détail d'implémentation, et le compilateur replie parfois les constantes d'un même fichier, ce qui change le résultat.

### 10.2 Mutable ou immuable : la seule question qui compte

| Immuables | Mutables |
|---|---|
| `int`, `float`, `bool`, `str`, `bytes`, `tuple`, `frozenset`, `None` | `list`, `dict`, `set`, `bytearray`, tes classes |

Un objet immuable ne change jamais. `a = a + 1` ne modifie pas 5, il crée 6. `s.upper()` ne modifie pas `s`, il renvoie une nouvelle chaîne. Toute opération sur un immuable renvoie un nouvel objet, et l'étiquette bouge.

Un objet mutable change **sur place**, et toutes les étiquettes qui le désignent voient le changement :

```python
>>> l1 = [1, 2, 3]
>>> l2 = l1            # pas une copie : une deuxième étiquette
>>> l2.append(4)
>>> l1
[1, 2, 3, 4]
```

> **Venant du C** : `l2 = l1` est `int *l2 = l1;`, pas `memcpy`. Toute affectation en Python copie un pointeur, jamais les données. Ce n'est pas plus dangereux qu'en C ; c'est juste qu'il n'y a pas d'autre mode.

Un tuple immuable peut contenir un mutable : `t = (1, [2, 3]); t[1].append(4)` marche. L'immuabilité porte sur les *étiquettes* que le tuple tient, pas sur les objets au bout.

### 10.3 Passage d'arguments : ni par valeur, ni par référence

Le débat « par valeur ou par référence » vient de C et de C++ et ne s'applique pas. Python passe **l'objet** : le paramètre devient une étiquette de plus sur l'objet donné en argument. Le comportement observé dépend alors uniquement de ce que la fonction fait, et de la mutabilité de l'objet.

```python
def ajoute(liste):
    liste.append(99)       # modifie l'objet partagé : l'appelant le voit

def incremente(n):
    n += 1                 # crée un nouvel int, l'étiquette LOCALE n bouge
    return n               # l'appelant ne voit rien sans ce return

def remplace(liste):
    liste = [0]            # rebind LOCAL : l'appelant ne voit rien non plus
```

```python
>>> L, N = [1], 1
>>> ajoute(L); incremente(N); remplace(L)
>>> L, N
([1, 99], 1)
```

La règle : **une méthode qui modifie sur place (`append`, `sort`, `update`, `pop`, `+=` sur une liste) est vue par tout le monde ; une affectation `x = ...` ne change qu'une étiquette locale.** C'est aussi pour ça que les défauts mutables (chapitre 5) sont un piège : le `[]` du `def f(x=[])` est un seul objet, créé une fois, partagé par tous les appels.

**`+=` n'est pas toujours ce qu'il semble.** Sur une liste, `+=` appelle `__iadd__` et modifie sur place. Sur un tuple, qui n'a pas d'`__iadd__`, Python fait `t = t + (3,)`, donc un nouvel objet :

```python
>>> l = [1, 2]; m = l; l += [3]; l is m
True
>>> t = (1, 2); u = t; t += (3,); t is u
False
```

### 10.4 Copier pour de vrai

```python
>>> grille = [[0] * 2] * 2          # une SEULE ligne, référencée deux fois
>>> grille[0][0] = 1
>>> grille
[[1, 0], [1, 0]]
>>> g2 = [[0] * 2 for _ in range(2)] # deux listes distinctes
>>> g2[0][0] = 1
>>> g2
[[1, 0], [0, 0]]
```

`[x] * n` répète l'étiquette, pas l'objet. Pour un tableau 2D, la compréhension.

Trois niveaux de copie :

| Écriture | Ce qu'elle fait |
|---|---|
| `b = a` | rien : une étiquette de plus |
| `b = a[:]`, `list(a)`, `a.copy()`, `copy.copy(a)` | **superficielle** : nouvelle liste, mêmes éléments (étiquettes copiées) |
| `b = copy.deepcopy(a)` | **profonde** : récursive, tout est dupliqué |

```python
>>> import copy
>>> orig = [[1, 2], [3, 4]]
>>> sup, prof = copy.copy(orig), copy.deepcopy(orig)
>>> orig[0].append(9)
>>> sup, prof
([[1, 2, 9], [3, 4]], [[1, 2], [3, 4]])
```

La copie superficielle suffit pour une liste d'immuables (nombres, chaînes). Dès qu'il y a des listes ou des dicts dedans, il faut `deepcopy`, ou repenser : souvent, ne pas copier du tout et ne pas muter (créer une nouvelle structure) est plus simple.

### 10.5 Comptage de références et ramasse-miettes

Chaque objet porte son `ob_refcnt`. Une étiquette de plus, +1 ; une étiquette qui disparaît (`del`, fin de fonction, réaffectation), -1. À zéro, l'objet est libéré **immédiatement**. C'est pour ça que Python n'a ni `free` ni pauses de GC à la Java dans le cas courant : la mémoire est rendue dès que plus personne ne s'en sert.

```python
>>> import sys
>>> orig = [[1, 2], [3, 4]]
>>> sys.getrefcount(orig)
2                      # l'étiquette orig + l'argument temporaire de getrefcount
```

Le comptage a un trou : les **cycles**. Si `a.other = b` et `b.other = a`, chacun garde l'autre à 1 même quand plus rien d'extérieur ne les désigne. Pour ça, CPython a en plus un ramasse-miettes générationnel (`import gc`) qui passe de temps en temps chercher les cycles inaccessibles. `gc.collect()` le force ; tu n'en as besoin que pour des mesures ou des tests.

`del x` ne détruit pas un objet, il retire une étiquette. Et `__del__` (le « destructeur ») s'exécute quand le compteur tombe à zéro, ce qui peut être jamais s'il y a un cycle, ou tard, ou pendant l'arrêt de l'interpréteur. Ne mets rien d'important dedans : pour fermer un fichier ou une connexion, c'est `with` (chapitre 11).

### 10.6 Le bytecode

Ton `.py` n'est pas interprété ligne par ligne. Il est **compilé** en bytecode, des instructions pour une machine virtuelle à pile, puis exécuté par une grande boucle en C dans CPython. Le module `dis` montre ce bytecode :

```python
>>> import dis
>>> def carre_plus_un(x):
...     y = x * x
...     return y + 1
...
>>> dis.dis(carre_plus_un)
  3           LOAD_FAST_LOAD_FAST      0 (x, x)
              BINARY_OP                5 (*)
              STORE_FAST               1 (y)

  4           LOAD_FAST                1 (y)
              LOAD_CONST               1 (1)
              BINARY_OP                0 (+)
              RETURN_VALUE
```

(La sortie exacte dépend de la version : 3.13 ici. Une ligne `RESUME` peut apparaître au début.)

Ça se lit comme de l'assembleur pour une machine sans registres : `LOAD_FAST` empile une variable locale, `LOAD_CONST` empile une constante, `BINARY_OP` dépile deux valeurs, calcule, rempile le résultat, `STORE_FAST` dépile dans une locale, `RETURN_VALUE` dépile et renvoie. Le numéro à gauche est la ligne source.

Chaque instruction coûte, dans la boucle C, un dispatch, une vérification de type (« `*` sur deux `int` ? deux `str` ? un objet avec `__mul__` ? »), une allocation du résultat, et de la comptabilité de références. Là où le C fait une instruction `mul`, Python en fait quelques centaines. C'est **la** raison de la lenteur, et c'est aussi ce qui permet `x * x` de marcher sur n'importe quel type sans rien déclarer.

Le bytecode est mis en cache dans `__pycache__/module.cpython-313.pyc` pour éviter de recompiler à chaque import. Le script principal n'est jamais mis en cache. Ces fichiers se suppriment sans risque.

### 10.7 Le GIL

CPython a un verrou global, le **GIL** (*Global Interpreter Lock*) : un seul thread exécute du bytecode à la fois. Le compteur de références de 10.5 n'est pas atomique ; sans ce verrou, deux threads qui incrémentent et décrémentent le même `ob_refcnt` corrompraient la mémoire. Le GIL a été le choix simple de 1992, et il a rendu CPython et ses milliers d'extensions C faciles à écrire.

La conséquence pratique, mesurée sur un M1 :

```python
def cpu(n):
    s = 0
    for i in range(n):
        s += i * i
    return s
```

| Deux fois `cpu(3_000_000)` | Temps |
|---|---|
| en séquence | 0,24 s |
| dans 2 threads | 0,25 s |
| dans 2 processus (`multiprocessing.Pool`) | 0,18 s |

Les threads n'apportent **rien** sur du calcul pur : ils se relaient sur le GIL. Ils apportent beaucoup dès que le programme **attend** (réseau, disque, `sleep`, sous-processus) : un thread qui attend relâche le GIL, et les autres tournent. Pour du calcul, on lance des **processus** (`multiprocessing`, `concurrent.futures.ProcessPoolExecutor`), chacun avec son interpréteur et son GIL, au prix d'un démarrage et d'une copie des données.

En résumé : I/O → threads, ou mieux, `asyncio` (chapitre 15). CPU → processus, ou une bibliothèque en C (10.8).

> **Piège** : `python3.13t`, le CPython « free-threaded » sans GIL, existe depuis 3.13 comme build expérimental (`sys._is_gil_enabled()` dit dans quel cas tu es). Il fait tourner les threads en vrai parallèle, mais une partie des extensions C ne le supporte pas encore et le code mono-thread est un peu plus lent. En 2026 c'est à surveiller, pas à utiliser en prod.

### 10.8 Performance : mesurer, puis les vraies réponses

D'abord mesurer. `timeit` exécute un bout de code plusieurs fois et donne le meilleur temps, ce qui neutralise le bruit :

```bash
$ python3 -m timeit -s "n = 1_000_000" "sum(range(n))"
20 loops, best of 5: 12 msec per loop
```

```python
import timeit
print(timeit.timeit(lambda: sum(range(1_000_000)), number=5) / 5)
```

Sur un million d'entiers, une boucle `for` avec `total += i` prend 27 ms, `sum(range(n))` 12 ms, `sum([i for i in range(n)])` 26 ms. La boucle de `sum` tourne en C ; la tienne tourne en bytecode. C'est le premier levier.

Les réponses, dans l'ordre où il faut les essayer :

1. **L'algorithme.** Un `in` sur une liste est O(n), sur un set O(1). Un tri suivi d'une recherche binaire bat vingt boucles imbriquées. Le passage de 100× lent à 100× rapide se joue là bien plus souvent que dans le langage.
2. **La bibliothèque standard.** `sum`, `min`, `sorted`, `str.join`, `dict`, `collections.Counter`, `itertools`, `re`, `json` : tout ça est en C. Une boucle Python qui refait ce qu'ils font est presque toujours plus lente.
3. **NumPy** pour le numérique : un tableau contigu d'entiers ou de flottants natifs (pas des `PyObject`), et des opérations vectorisées en C. `a * a` sur un million d'éléments, c'est une instruction Python et une boucle C.
4. **Un autre interpréteur** : PyPy, avec un compilateur JIT, fait tourner du Python pur 4 à 10 fois plus vite. Pas toutes les extensions C.
5. **Écrire la partie chaude en C** : Cython (du Python annoté compilé en C), ou une extension écrite en Rust avec PyO3. C'est ce que font NumPy, pydantic, orjson, polars.
6. **Appeler une bibliothèque C existante** avec `ctypes`, dans la boîte :

```python
import ctypes

libc = ctypes.CDLL(None)                  # la libc déjà chargée (macOS, Linux)
libc.strlen.argtypes = [ctypes.c_char_p]  # prototype : ce que C attend
libc.strlen.restype = ctypes.c_size_t     # et ce qu'il renvoie

>>> libc.strlen(b"hello")                 # bytes, pas str : C veut des char*
5
>>> libc.getpid()
92957
```

`ctypes` te donne les types C (`c_int`, `c_char_p`, `POINTER`, `Structure`) et charge n'importe quelle `.so`/`.dylib`/`.dll`. Déclarer `argtypes` et `restype` n'est pas optionnel : sans, `ctypes` devine, et sur un pointeur 64 bits il devine mal.

Et la réponse la plus fréquente : **ce n'est pas lent**. Un script d'infra qui lit un JSON, appelle une API et écrit un rapport passe 99 % de son temps à attendre le réseau. Le temps d'exécution du bytecode n'y change rien. Mesure avant d'optimiser.

### 10.9 Ce qu'il faut retenir

- Une variable est une étiquette sur un objet. L'affectation copie une étiquette, jamais des données. `is` compare les étiquettes, `==` les valeurs.
- Immuable : toute opération crée un nouvel objet. Mutable : modification sur place, vue par toutes les étiquettes, y compris à travers un appel de fonction.
- Copier pour de vrai : `copy.copy` (superficielle) ou `copy.deepcopy` (profonde). `[x] * n` répète une étiquette.
- Comptage de références : libération immédiate ; le GC ne sert qu'aux cycles. `__del__` n'est pas fiable, `with` l'est.
- Le `.py` est compilé en bytecode (`dis.dis`), exécuté par une boucle C. Chaque instruction porte le coût du typage dynamique.
- Le GIL : un thread de bytecode à la fois. Threads pour l'attente, processus pour le calcul, bibliothèques en C pour les deux.
- Mesure avec `timeit`. Puis : algorithme, stdlib, NumPy, PyPy, Cython/Rust, `ctypes`.

**Labo 10** : une série d'expériences à prédire avant de lancer : références, copies, `+=`, `dis`, `timeit`, `ctypes`.

---

← [9. Classes et objets](09-classes-et-objets.md) · [Sommaire](../README.md) · [11. Itérateurs, générateurs, décorateurs, `with`](11-iterateurs-generateurs-decorateurs.md) →
