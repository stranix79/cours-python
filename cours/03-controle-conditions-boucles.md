# 3. Contrôle : conditions et boucles

*Python de zéro à FastAPI — chapitre 3 sur 21.* ← [2. Variables, types, chaînes](02-variables-types-chaines.md) · [Sommaire](../README.md) · [4. Collections : listes, tuples, dicts, sets](04-collections.md) →

> 🧪 Labo associé : [`labs/03-devine-nombre`](../labs/03-devine-nombre/README.md)

### 3.1 L'indentation est la syntaxe

En C, les accolades délimitent un bloc et l'indentation est décorative. En Python, c'est l'inverse : **il n'y a pas d'accolades, le bloc est défini par l'indentation**. Un deux-points `:` ouvre le bloc, les lignes qui suivent, indentées d'un cran, en font partie, la première ligne moins indentée le ferme.

```python
if temperature > 30:
    print("chaud")          # dans le if
    print("très chaud")     # toujours dans le if
print("fin")                # hors du if
```

Ça a une conséquence heureuse : le code que tu *lis* est le code qui *s'exécute*. Le bug classique du C, `if (x) instruction1; instruction2;` avec `instruction2` alignée sous `instruction1` mais hors du `if`, est impossible en Python.

> **Piège** : 4 espaces par niveau, jamais de tabulations. Un fichier qui mélange les deux donne `TabError: inconsistent use of tabs and spaces in indentation`, et un fichier qui mélange 2 et 4 espaces donne `IndentationError`. Règle ton éditeur une fois pour toutes (chapitre 1) et n'y pense plus.

Il n'y a pas de bloc vide : si tu as besoin d'un `if` ou d'une fonction qui ne fait rien encore, écris `pass`, l'instruction qui ne fait rien. Tu en verras dans les squelettes des labos.

### 3.2 `if`, `elif`, `else`

```python
code = 137
if code == 0:
    etat = "succès"
elif code > 128:
    etat = f"tué par le signal {code - 128}"
elif code == 127:
    etat = "commande introuvable"
else:
    etat = "erreur"
```

Pas de parenthèses autour de la condition (elles ne gênent pas, mais on ne les met pas), `elif` plutôt que `else if`, et `==` pour comparer. Le `=` dans une condition est une erreur de syntaxe, pas un bug silencieux :

```python
>>> if x = 5: pass
SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?
```

Les comparaisons se chaînent comme en maths : `0 <= x < 10` veut dire `0 <= x and x < 10`. Et le ternaire se lit comme une phrase :

```python
parite = "pair" if n % 2 == 0 else "impair"
```

### 3.3 Vrai, faux, et tout ce qui compte comme tel

Toute valeur peut servir de condition. Est **faux** : `False`, `None`, zéro (`0`, `0.0`), et tout ce qui est **vide** (`""`, `[]`, `{}`, `()`, `set()`). Est vrai tout le reste, y compris `"False"` (une chaîne non vide) et `[0]` (une liste non vide).

```python
>>> bool(0), bool(""), bool([]), bool(None)
(False, False, False, False)
>>> bool("False"), bool([0]), bool(-1)
(True, True, True)
```

C'est pour ça qu'on écrit `if lignes:` plutôt que `if len(lignes) > 0:`, et `if not nom:` plutôt que `if nom == "":`. C'est idiomatique, c'est lisible, et ça marche pour toutes les collections.

Les opérateurs logiques sont des mots : `and`, `or`, `not`. Et ils ne renvoient pas `True`/`False` mais **le dernier opérande évalué**, avec court-circuit :

```python
>>> 0 or "défaut", "" or "défaut", "x" or "défaut"
('défaut', 'défaut', 'x')
>>> 1 and 2, 0 and 2
(2, 0)
```

`a or b` renvoie `a` s'il est vrai, sinon `b`. D'où l'idiome `port = config_port or 8080` : la valeur par défaut si l'autre est vide ou `None`. Le court-circuit est le même qu'en C : dans `x is not None and x.startswith("a")`, la deuxième partie n'est jamais évaluée si `x` est `None`.

> **Piège** : `None == 0` est `False`, `None == False` est `False`, mais `not None` est `True`. `None` est faux *en tant que condition*, sans être égal à quoi que ce soit. Teste-le toujours avec `is None` / `is not None`.

### 3.4 `while`

```python
essais = 0
while essais < 3:
    essais += 1          # pas de ++ en Python
```

Rien de neuf par rapport au C, à deux détails près : pas de `do … while` (on écrit `while True:` avec un `break` dedans), et pas de `++` (`i += 1`). Le `while True:` n'est pas un code smell en Python, c'est la façon normale d'écrire une boucle « jusqu'à ce que ».

### 3.5 `for` : sur un itérable, jamais sur un compteur

Voici la différence qui change la façon d'écrire. Le `for` de Python n'est pas `for (i = 0; i < n; i++)`. C'est un `foreach` : il parcourt les éléments d'une collection, un par un, sans index.

```python
serveurs = ["web1", "web2", "db1"]
for serveur in serveurs:
    print(serveur)
```

> **Venant du C** : le réflexe `for i in range(len(serveurs)): print(serveurs[i])` marche, mais c'est du C traduit. On ne parcourt pas les indices pour aller chercher les éléments ; on parcourt les éléments. Si on a *aussi* besoin de l'indice, `enumerate` le donne en même temps.

Quand on veut vraiment compter, `range` fabrique la suite d'entiers, avec la même convention « début inclus, fin exclue » que le slicing :

```python
>>> list(range(5)), list(range(2, 10, 3)), list(range(10, 0, -3))
([0, 1, 2, 3, 4], [2, 5, 8], [10, 7, 4, 1])
```

`range(10)` n'est pas une liste : c'est un objet paresseux qui produit les nombres à la demande. `range(10 ** 9)` ne consomme pas 8 Go, et `5 in range(10)` est instantané. On en reparle au chapitre 11.

Deux compagnons du `for` à connaître dès maintenant :

```python
>>> for i, nom in enumerate(["web", "db"], start=1):
...     print(i, nom)
1 web
2 db
>>> for hote, ip in zip(["web", "db"], ["10.0.0.1", "10.0.0.2"]):
...     print(hote, ip)
web 10.0.0.1
db 10.0.0.2
```

`enumerate` donne l'indice et l'élément ; `zip` avance en parallèle dans plusieurs collections et s'arrête à la plus courte. La forme `for i, nom in …` dépaquette le couple `(i, nom)` à chaque tour, on y revient au chapitre 4.

`for` parcourt **tout ce qui est itérable** : une liste, une chaîne (caractère par caractère), un dictionnaire (ses clés), un fichier ouvert (ligne par ligne, chapitre 7), la sortie d'une commande, un générateur… C'est un des mécanismes centraux du langage.

### 3.6 `break`, `continue`, et le `else` de boucle

`break` sort de la boucle, `continue` saute au tour suivant, comme en C. Et il y a une chose que le C n'a pas : une clause **`else` sur une boucle**, exécutée **si la boucle s'est terminée sans `break`**.

```python
for n in [3, 5, 7]:
    if n % 2 == 0:
        print("pair trouvé")
        break
else:
    print("aucun pair")
```

```
aucun pair
```

> **Piège** : ce `else` ne veut pas dire « si la liste est vide ». Il veut dire « pas de `break` ». Lis-le comme « `nobreak` ». C'est exactement le cas « recherche sans succès » qu'on gère en C avec un booléen `trouve` initialisé à 0 avant la boucle.

### 3.7 `match` : le `switch` en mieux

Depuis Python 3.10, `match` compare une valeur à une suite de **motifs**, du haut vers le bas, et exécute le premier qui colle. Sur des constantes, c'est un `switch` sans `break` à oublier :

```python
def statut(code: int) -> str:
    match code:
        case 0:
            return "OK"
        case 1 | 2:                          # ou
            return "erreur mineure"
        case 127:
            return "commande introuvable"
        case n if n > 128:                   # capture + garde
            return f"tué par le signal {n - 128}"
        case _:                              # défaut
            return "erreur"
```

Mais un motif peut aussi **décomposer** une structure, et c'est là que `match` dépasse le `switch` :

```python
def executer(argv: list[str]) -> str:
    match argv:
        case ["ls"]:
            return "liste ."
        case ["ls", chemin]:
            return f"liste {chemin}"
        case ["cp", src, dst]:
            return f"copie {src} -> {dst}"
        case ["rm", *fichiers]:
            return f"supprime {len(fichiers)} fichier(s)"
        case _:
            return "commande inconnue"
```

```python
>>> executer(["cp", "a", "b"]), executer(["rm", "a", "b", "c"]), executer(["mv"])
('copie a -> b', 'supprime 3 fichier(s)', 'commande inconnue')
```

Le motif `["cp", src, dst]` vérifie « une liste de trois éléments dont le premier est `"cp"` » et lie `src` et `dst` au passage. Ça marche aussi sur les dictionnaires (`case {"host": h, "port": 80}:`) et les objets (chapitre 9). Un nom nu dans un motif **capture** toujours, il ne compare pas : `case erreur:` attrape tout et s'appelle `erreur`. Pour comparer à une constante nommée, il faut un point : `case Codes.OK:`.

Quand faut-il un `match` plutôt qu'une cascade de `if/elif` ? Quand on décompose une structure (arguments, message JSON, événement), ou quand il y a plus de trois ou quatre cas sur la même valeur. Pour deux cas, `if` reste plus lisible.

### 3.8 Le morse `:=`

L'opérateur d'affectation en expression (walrus, « morse », parce qu'il ressemble à des yeux et des défenses) affecte *et* renvoie la valeur. Il évite de répéter un appel :

```python
import re
if (m := re.search(r"\d+", "port 8080")):
    print(m.group())          # 8080
```

Sans lui, on écrirait `m = re.search(...)` sur une ligne puis `if m:` sur la suivante. Il sert surtout dans les `while` qui lisent jusqu'à épuisement (`while (bloc := f.read(4096)):`) et les compréhensions (chapitre 4). Ne l'utilise pas ailleurs : deux lignes claires valent mieux qu'une ligne maline.

### 3.9 Ce qu'il faut retenir

- Pas d'accolades : `:` ouvre un bloc, l'indentation (4 espaces) le délimite. `pass` pour un bloc vide.
- `if` / `elif` / `else`, comparaisons chaînées, ternaire `a if cond else b`.
- Vide, zéro et `None` sont faux ; `and` / `or` renvoient un opérande, pas un booléen, d'où `x or défaut`.
- `for` parcourt un itérable, pas un compteur. `range`, `enumerate`, `zip` couvrent les cas où on compte.
- `else` sur une boucle = « terminée sans `break` ».
- `match` fait du `switch` **et** de la décomposition de structures.

**Labo 03** : un jeu « devine le nombre » (boucle `while`, comparaisons, compteur), un FizzBuzz, puis un mini analyseur de lignes de log nginx avec `match`.

---

← [2. Variables, types, chaînes](02-variables-types-chaines.md) · [Sommaire](../README.md) · [4. Collections : listes, tuples, dicts, sets](04-collections.md) →
