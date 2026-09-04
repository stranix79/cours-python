# 4. Collections : listes, tuples, dicts, sets

*Python de zéro à FastAPI — chapitre 4 sur 21.* ← [3. Contrôle : conditions et boucles](03-controle-conditions-boucles.md) · [Sommaire](../README.md) · [5. Fonctions](05-fonctions.md) →

> 🧪 Labo associé : [`labs/04-inventaire`](../labs/04-inventaire/README.md)

En C, tu as le tableau, et tout le reste (liste chaînée, table de hachage, ensemble) tu l'écris toi-même ou tu l'empruntes. Python livre quatre structures dans le langage, avec une syntaxe littérale pour chacune. Les connaître et choisir la bonne est 80 % du Python idiomatique.

| | Littéral | Ordonnée | Modifiable | Doublons | Usage |
|---|---|---|---|---|---|
| `list` | `[1, 2, 3]` | oui | oui | oui | une séquence qui grandit |
| `tuple` | `(1, 2, 3)` | oui | non | oui | un enregistrement fixe, un retour multiple |
| `dict` | `{"a": 1}` | insertion | oui | clés uniques | associer des clés à des valeurs |
| `set` | `{1, 2, 3}` | non | oui | non | unicité, appartenance, opérations ensemblistes |

### 4.1 `list`

Une liste est un **tableau dynamique** d'objets quelconques (pas forcément du même type, même si en pratique on s'y tient) :

```python
>>> serveurs = ["web1", "web2", "db1"]
>>> serveurs.append("db2")          # à la fin, O(1)
>>> serveurs.insert(0, "lb1")       # au début, O(n) : tout se décale
>>> serveurs
['lb1', 'web1', 'web2', 'db1', 'db2']
>>> serveurs.pop()                  # retire et renvoie le dernier
'db2'
>>> serveurs.pop(0)                 # retire et renvoie le premier, O(n)
'lb1'
>>> serveurs.remove("web2")         # par valeur (la première occurrence)
>>> serveurs.extend(["cache1", "cache2"])
>>> serveurs.index("db1"), serveurs.count("db1"), len(serveurs), "web1" in serveurs
(1, 1, 4, True)
```

L'indexation et le slicing sont ceux des chaînes (chapitre 2), à ceci près qu'une liste est **modifiable** : `l[0] = "x"` marche, `l[0:2] = [9, 9, 9]` remplace deux éléments par trois, `del l[0]` supprime.

> **Venant du C** : sous le capot, une `list` est un tableau de **pointeurs** vers des objets, avec une capacité réservée un peu plus grande que la taille pour que `append` soit amorti en O(1). C'est un `realloc` intelligent. L'accès `l[i]` est en O(1) ; l'insertion au début est en O(n) comme un `memmove`. Si tu as besoin d'une file (ajouter d'un côté, retirer de l'autre), c'est `collections.deque`.

**Trier.** Deux façons, et la différence est importante :

```python
>>> l = [3, 1, 2]
>>> sorted(l)                       # renvoie une NOUVELLE liste triée
[1, 2, 3]
>>> l.sort()                        # trie SUR PLACE et renvoie None
>>> l
[1, 2, 3]
```

> **Piège** : `l = l.sort()` met `None` dans `l`. Les méthodes qui modifient sur place (`sort`, `append`, `reverse`, `extend`) renvoient `None`, précisément pour qu'on ne les confonde pas avec celles qui renvoient une copie. `sorted()` marche sur n'importe quel itérable et renvoie toujours une liste.

Le tri prend une **clé** : une fonction appliquée à chaque élément pour décider de l'ordre. On y met souvent un `lambda` (une fonction anonyme d'une ligne, chapitre 5) :

```python
>>> serveurs = [("web1", 16), ("db1", 64), ("web2", 8)]
>>> sorted(serveurs, key=lambda s: s[1])              # par RAM croissante
[('web2', 8), ('web1', 16), ('db1', 64)]
>>> sorted(serveurs, key=lambda s: (-s[1], s[0]))     # RAM décroissante, puis nom
[('db1', 64), ('web1', 16), ('web2', 8)]
>>> max(serveurs, key=lambda s: s[1])
('db1', 64)
>>> sorted(["b", "A", "c"]), sorted(["b", "A", "c"], key=str.lower)
(['A', 'b', 'c'], ['A', 'b', 'c'])
```

Une clé qui renvoie un tuple trie par le premier élément, puis le deuxième en cas d'égalité : c'est comme ça qu'on fait un `ORDER BY ram DESC, nom`. Le tri est **stable** (deux éléments égaux gardent leur ordre), et c'est un Timsort, O(n log n).

**Copie et référence.** Le point où le C te trahit :

```python
>>> a = [1, 2, 3]
>>> b = a                  # b est une deuxième étiquette sur LA MÊME liste
>>> b.append(4)
>>> a
[1, 2, 3, 4]
>>> c = a.copy()           # (ou a[:], ou list(a)) : une nouvelle liste
>>> c.append(5)
>>> a
[1, 2, 3, 4]
```

`b = a` ne copie rien. En C, tu aurais deux pointeurs sur le même tableau, et ça te semblerait normal ; ici la syntaxe ressemble à une copie de valeur, et ce n'en est pas une. Le chapitre 10 est consacré à cette question ; en attendant, retiens : **l'affectation ne copie jamais, `.copy()` copie le premier niveau.**

### 4.2 `tuple`

Un tuple est une séquence **immuable**. Les parenthèses sont facultatives, c'est la virgule qui fait le tuple :

```python
>>> t = 1, 2, 3
>>> t[0], t[1:], len(t)
(1, (2, 3), 3)
>>> t[0] = 9
TypeError: 'tuple' object does not support item assignment
>>> type((1,)), type((1))           # (1,) est un tuple, (1) est un int
(<class 'tuple'>, <class 'int'>)
```

À quoi sert une liste qu'on ne peut pas modifier ? À trois choses. Un **enregistrement** hétérogène à structure fixe (`("web1", "10.0.0.1", 16)`), là où une liste est une collection homogène de longueur variable. Une **clé de dictionnaire** (une liste ne peut pas l'être, on voit pourquoi en 4.3). Et le **retour multiple** d'une fonction :

```python
def minmax(valeurs):
    return min(valeurs), max(valeurs)      # renvoie un tuple

lo, hi = minmax([4, 9, 1])                 # dépaqueté à la réception
```

Ce **dépaquetage** (unpacking) marche partout où il y a une séquence à droite et des noms à gauche, avec une étoile pour « tout le reste » :

```python
>>> x, y, *reste = 1, 2, 3, 4
>>> x, y, reste
(1, 2, [3, 4])
>>> premier, *_, dernier = [1, 2, 3, 4, 5]
>>> premier, dernier
(1, 5)
```

C'est ce qui se passe dans `for i, nom in enumerate(...)` et dans `a, b = b, a`. Le `_` est un nom comme un autre, par convention « je n'en ai pas besoin ».

> **Venant du C** : le tuple est le `struct` du pauvre, sans noms de champs. Quand les champs méritent un nom, `namedtuple` (4.6) ou une `dataclass` (chapitre 9) font le même travail en lisible.

### 4.3 `dict`

Le dictionnaire est **la** structure de Python. Une table de hachage qui associe des clés à des valeurs, en O(1) pour lire, écrire, tester la présence. Les objets, les modules, les espaces de noms : en interne, tout est dict.

```python
>>> ips = {"web1": "10.0.0.1", "db1": "10.0.0.2"}
>>> ips["web2"] = "10.0.0.3"               # ajout ou remplacement
>>> ips["web1"]
'10.0.0.1'
>>> ips["x"]
KeyError: 'x'
>>> ips.get("x"), ips.get("x", "inconnue")  # sans exception, avec défaut
(None, 'inconnue')
>>> "web1" in ips, len(ips)                 # in teste les CLÉS
(True, 3)
>>> ips.pop("web2")
'10.0.0.3'
```

Depuis Python 3.7, un dict **conserve l'ordre d'insertion**. Ce n'est pas un détail : un JSON lu puis réécrit garde l'ordre de ses champs, et `list(d)` donne les clés dans l'ordre où on les a mises.

Parcourir :

```python
for hote in ips:                      # les clés
    ...
for hote, ip in ips.items():          # les couples, dépaquetés
    print(f"{hote} → {ip}")
list(ips.keys()), list(ips.values())
```

Deux méthodes qui remplacent des `if` :

```python
>>> ips.setdefault("web3", "10.0.0.9")    # insère si absent, renvoie la valeur
'10.0.0.9'
>>> ips.update({"web1": "10.0.0.100"})     # fusionne (écrase les clés existantes)
>>> ips | {"lb1": "10.0.0.250"}            # nouveau dict fusionné (3.9+)
```

**Les clés doivent être hachables** : immuables, en pratique `str`, `int`, `float`, `bool`, `tuple` (de hachables), `frozenset`. Une liste ne l'est pas :

```python
>>> {[1, 2]: "x"}
TypeError: unhashable type: 'list'
>>> {(1, 2): "ok"}
{(1, 2): 'ok'}
```

Pourquoi ? Le dict range une clé dans une case calculée à partir de son hash. Si la clé changeait après coup, son hash changerait, et on ne la retrouverait plus. Une clé immuable est une clé dont le hash est stable.

> **Venant de Java** : c'est une `HashMap<Object, Object>` avec une syntaxe littérale, l'ordre d'insertion en plus, et `==` qui compare le contenu. Les clés sont typiquement des chaînes ; un dict avec des clés fixes joue souvent le rôle qu'un objet jouerait en Java (et on verra au chapitre 9 quand il vaut mieux une vraie classe).

### 4.4 `set`

Un ensemble : des éléments **uniques**, sans ordre, hachables. C'est un dict sans valeurs, avec les mêmes performances.

```python
>>> s = {3, 1, 2, 3, 1}
>>> s, len(s), 2 in s
({1, 2, 3}, 3, True)
>>> set("hello")
{'o', 'l', 'h', 'e'}
>>> a, b = {1, 2, 3}, {2, 3, 4}
>>> a | b, a & b, a - b, a ^ b             # union, intersection, différence, différence symétrique
({1, 2, 3, 4}, {2, 3}, {1}, {1, 4})
>>> a <= {1, 2, 3, 4}                      # inclusion
True
>>> s.add(9); s.discard(42)                # discard n'échoue pas si absent, remove si
```

Trois usages quotidiens : **dédoublonner** (`set(liste)`), **tester l'appartenance** en O(1) là où `x in liste` est en O(n), et **comparer deux inventaires** (« quels hôtes sont dans le DNS mais pas dans Ansible ? » → `dns - ansible`). Attention, `{}` est un dict vide ; l'ensemble vide s'écrit `set()`.

### 4.5 Les compréhensions

Une compréhension construit une collection à partir d'un itérable, en une expression. C'est du `for` avec un filtre, écrit dans l'ordre où on le lit à voix haute :

```python
>>> [x * x for x in range(5)]
[0, 1, 4, 9, 16]
>>> [x for x in range(10) if x % 2 == 0]
[0, 2, 4, 6, 8]
>>> {nom: len(nom) for nom in ["web1", "db1"]}
{'web1': 4, 'db1': 3}
>>> {x % 3 for x in range(10)}
{0, 1, 2}
>>> sum(x for x in range(10))              # sans crochets : un générateur (chapitre 11)
45
```

La version boucle de la première :

```python
carres = []
for x in range(5):
    carres.append(x * x)
```

Quatre lignes contre une, et la compréhension dit *ce qu'on construit* avant *comment*. La règle : une compréhension pour une transformation ou un filtre simple, une boucle dès qu'il y a plus d'une condition ou un effet de bord. Une compréhension sur trois lignes avec deux `for` et un `if`, c'est une boucle qui a honte.

> **Piège** : `[[0] * 3] * 2` fait deux fois **la même** liste interne. `m[0][0] = 1` modifie les deux lignes. La bonne façon : `[[0] * 3 for _ in range(2)]`, qui évalue `[0] * 3` deux fois. Encore l'histoire des références.

### 4.6 `collections` : les trois qu'on utilise vraiment

```python
>>> from collections import Counter, defaultdict, namedtuple
>>> Counter("mississippi").most_common(2)
[('i', 4), ('s', 4)]
```

**`Counter`** compte les occurrences : donne-lui un itérable, il rend un dict `élément → nombre`, avec `most_common()` et une valeur `0` pour les clés absentes. C'est le `sort | uniq -c | sort -rn` du shell.

```python
>>> par_os = defaultdict(list)
>>> par_os["debian"].append("web1")        # la clé n'existait pas : créée avec list()
>>> par_os["debian"].append("web2")
>>> dict(par_os)
{'debian': ['web1', 'web2']}
```

**`defaultdict(fabrique)`** appelle `fabrique()` pour créer la valeur d'une clé absente. Regrouper des éléments par catégorie devient une ligne par élément, sans `if cle not in d: d[cle] = []`.

```python
>>> Serveur = namedtuple("Serveur", ["nom", "ip", "ram"])
>>> s = Serveur("web1", "10.0.0.1", 16)
>>> s.ram, s[2], s._asdict()
(16, 16, {'nom': 'web1', 'ip': '10.0.0.1', 'ram': 16})
```

**`namedtuple`** est un tuple dont les champs ont un nom : `s.ram` au lieu de `s[2]`. Immuable, léger, lisible. Au chapitre 9, `dataclass` fera la même chose en modifiable et avec des types.

### 4.7 Choisir

| Besoin | Structure | Pourquoi |
|---|---|---|
| garder l'ordre, ajouter à la fin, indexer | `list` | O(1) en accès et en `append` |
| « est-ce que X est dedans ? » souvent | `set` (ou `dict`) | O(1), contre O(n) pour une liste |
| associer une valeur à une clé | `dict` | O(1) |
| un enregistrement à champs fixes | `tuple` / `namedtuple` | immuable, hachable, dépaquetable |
| compter | `Counter` | |
| regrouper | `defaultdict(list)` | |
| ajouter/retirer aux deux bouts | `collections.deque` | O(1) des deux côtés |
| dédoublonner en gardant l'ordre | `list(dict.fromkeys(l))` | un dict garde l'ordre, un set non |

Le réflexe qui vient du C, c'est de tout mettre dans une liste et de chercher dedans avec une boucle. Le réflexe Python, c'est : si tu cherches par clé, c'est un dict ; si tu testes l'appartenance, c'est un set ; si tu retournes plusieurs valeurs, c'est un tuple.

### 4.8 Ce qu'il faut retenir

- `list` : tableau dynamique, modifiable, `append`/`pop` en O(1) à la fin. `sorted()` renvoie une copie, `.sort()` trie sur place et renvoie `None`.
- `tuple` : immuable, la virgule fait le tuple, dépaquetage `a, b = …` et `*reste`.
- `dict` : table de hachage O(1), ordre d'insertion conservé, clés hachables (pas de liste). `get`, `setdefault`, `items`.
- `set` : unicité et appartenance en O(1), opérations `|` `&` `-`.
- Compréhensions `[f(x) for x in it if cond]` pour transformer et filtrer.
- `b = a` ne copie pas. Jamais.

**Labo 04** : un inventaire de serveurs à filtrer, trier, regrouper par OS, sommer, dédoublonner, avec listes de dicts, `Counter`, `defaultdict` et compréhensions.

---

← [3. Contrôle : conditions et boucles](03-controle-conditions-boucles.md) · [Sommaire](../README.md) · [5. Fonctions](05-fonctions.md) →
