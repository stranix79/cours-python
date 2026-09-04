# 2. Variables, types, chaînes

*Python de zéro à FastAPI — chapitre 2 sur 21.* ← [1. Installer, outiller, lancer](01-installer-et-outiller.md) · [Sommaire](../README.md) · [3. Contrôle : conditions et boucles](03-controle-conditions-boucles.md) →

> 🧪 Labo associé : [`labs/02-convertisseur`](../labs/02-convertisseur/README.md)

### 2.1 Une affectation est une étiquette

```python
>>> n = 42
>>> nom = "stranix"
>>> n = "quarante-deux"
```

Pas de déclaration, pas de type devant le nom. La troisième ligne est légale : `n` n'est pas une case de 4 octets typée `int`, c'est une **étiquette** qu'on colle sur un objet. L'objet `42` a un type ; l'étiquette n'en a pas. Recoller l'étiquette sur une chaîne ne pose aucun problème, et l'objet `42` orphelin sera libéré par le ramasse-miettes (chapitre 10).

> **Venant du C** : `int n = 42;` réserve de la mémoire *et* fixe le type pour toujours. En Python, `n = 42` fait deux choses : crée un objet `int` valant 42 quelque part sur le tas, puis lie le nom `n` à cet objet dans un dictionnaire de noms. On peut le voir : `id(n)` donne l'adresse de l'objet, `type(n)` son type. La variable elle-même n'a ni adresse fixe ni taille.

Conventions : `snake_case` pour les variables et fonctions (`nb_essais`, pas `nbEssais`), `MAJUSCULES` pour ce qu'on considère comme constant (`MAX_RETRIES = 3`, mais rien n'empêche de le modifier : Python n'a pas de `const`), `_prefixe` pour « usage interne, ne touche pas ».

On peut affecter plusieurs noms d'un coup, et échanger sans variable temporaire :

```python
>>> a, b = 1, 2
>>> a, b = b, a
>>> a, b
(2, 1)
```

### 2.2 Les nombres

**`int`** : entier de précision illimitée. Pas de 32 ou 64 bits, pas de débordement, pas de `long long`.

```python
>>> 2 ** 64
18446744073709551616
>>> 10 ** 100 % 7
4
>>> 1_000_000, 0b1010, 0o17, 0xFF      # séparateur visuel, binaire, octal, hexa
(1000000, 10, 15, 255)
```

L'objet grossit tout seul : `sys.getsizeof(0)` fait 28 octets, `sys.getsizeof(2 ** 1000)` en fait 160. C'est le prix de l'illimité, et il n'a d'importance que pour des millions de nombres (chapitre 10).

**`float`** : double IEEE 754 sur 64 bits, exactement le `double` du C, avec les mêmes limites.

```python
>>> 0.1 + 0.2
0.30000000000000004
>>> 0.1 + 0.2 == 0.3
False
>>> import math
>>> math.isclose(0.1 + 0.2, 0.3)
True
>>> 2 ** 53 + 1, float(2 ** 53 + 1)
(9007199254740993, 9007199254740992.0)
```

Ce n'est pas un bug de Python, c'est le binaire : 0.1 n'a pas de représentation finie en base 2, comme 1/3 n'en a pas en base 10. Pour de l'argent, on utilise `decimal.Decimal("0.1")`, jamais un `float`.

**Les opérateurs** qui surprennent venant du C :

| Expression | Résultat | Commentaire |
|---|---|---|
| `7 / 2` | `3.5` | `/` donne **toujours** un `float`, même `10 / 2` → `5.0` |
| `7 // 2` | `3` | division entière (arrondi vers le bas) |
| `-7 // 2` | `-4` | vers le bas, pas vers zéro comme en C (`-3`) |
| `-7 % 3` | `2` | le reste a le signe du **diviseur** (en C : `-1`) |
| `divmod(17, 5)` | `(3, 2)` | quotient et reste d'un coup |
| `2 ** 10` | `1024` | puissance ; `2 ** 0.5` → racine carrée |
| `2 ** -1` | `0.5` | |

Le `//` et le `%` de Python respectent l'identité `a == (a // b) * b + a % b` avec un reste toujours positif pour `b > 0`. C'est ce qu'on veut pour des indices circulaires ou des calendriers, et c'est pour ça que ça diffère du C.

**`bool`** : `True` et `False`, avec majuscule. C'est une sous-classe de `int` (`True + True` vaut `2`, ça sert pour compter). **`None`** : l'absence de valeur, le `NULL` du C mais qui est un vrai objet, unique. On teste avec `is None`, pas `== None` (le pourquoi au chapitre 10).

**Conversions** explicites, toujours par appel de fonction, jamais de cast implicite entre nombre et texte :

```python
>>> int("42"), int("2a", 16), int(3.99), float("1e3"), str(3.0)
(42, 42, 3, 1000.0, '3.0')
>>> round(2.675, 2), round(2.5), round(3.5)
(2.67, 2, 4)
>>> 5 + "cinq"
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

`int(3.99)` tronque vers zéro. `round()` arrondit au pair le plus proche sur les `.5` (arrondi bancaire, pour ne pas biaiser les sommes) ; et `round(2.675, 2)` donne `2.67` parce que 2.675 est en réalité `2.67499999…` en binaire. Toujours cette histoire d'IEEE 754.

> **Piège** : `1 == 1.0` est `True` (comparaison numérique), mais `3 == "3"` est `False` sans erreur. Python compare un `int` et un `str` sans broncher, et répond « pas égaux ». Pas de conversion sauvage, mais pas d'avertissement non plus.

### 2.3 Lire au clavier

```python
reponse = input("Température ? ")     # affiche l'invite, renvoie une str
temperature = float(reponse)          # à toi de convertir
```

`input()` renvoie **toujours** une chaîne, même si l'utilisateur tape `42`. Il faut convertir, et la conversion plante (`ValueError`) si le texte n'est pas un nombre. On apprendra à s'en protéger au chapitre 8 ; pour l'instant, on tape des choses valides.

### 2.4 Les chaînes

Une `str` est une suite de **caractères Unicode** (pas d'octets, on y revient en 2.7), immuable, avec des guillemets simples ou doubles au choix :

```python
>>> "Il a dit \"salut\"", 'l\'été', r"C:\temp\new"
('Il a dit "salut"', "l'été", 'C:\\temp\\new')
```

Le préfixe `r` (raw) désactive les séquences d'échappement : indispensable pour les expressions régulières et les chemins Windows. Trois guillemets ouvrent une chaîne multi-lignes, qui sert aussi de docstring (chapitre 5) :

```python
message = """Bonjour,
ceci tient sur
plusieurs lignes."""
```

**Indexation et slicing.** L'index commence à 0, un index négatif compte depuis la fin, et une tranche `[début:fin:pas]` prend de `début` **inclus** à `fin` **exclu** :

```python
>>> s = "Python"
>>> s[0], s[-1], s[1:4], s[:2], s[2:], s[::2], s[::-1]
('P', 'n', 'yth', 'Py', 'thon', 'Pto', 'nohtyP')
```

La convention « fin exclue » fait que `s[:n] + s[n:]` redonne `s` et que `len(s[a:b])` vaut `b - a`. Le slicing marche à l'identique sur les listes et les tuples (chapitre 4), autant s'y habituer tout de suite.

**Immuable.** On ne modifie pas une chaîne, on en fabrique une nouvelle :

```python
>>> s[0] = "J"
TypeError: 'str' object does not support item assignment
>>> s = "J" + s[1:]          # nouvelle chaîne, l'étiquette s est recollée dessus
```

> **Venant du C** : pas de `char buf[256]` qu'on remplit, pas de `\0` terminal, pas de `strcpy`, pas de dépassement de tampon. `len(s)` est en O(1), la longueur est stockée dans l'objet. Et `s1 + s2` alloue une troisième chaîne : dans une boucle qui concatène des milliers de morceaux, on préfère accumuler dans une liste et faire `"".join(morceaux)` à la fin.

**Les méthodes** qu'on utilise dix fois par jour. Elles renvoient toutes une nouvelle chaîne (ou autre chose), jamais elles ne modifient `s` :

```python
>>> s = "  Bonjour le monde  "
>>> s.strip()                      # enlève blancs (espaces, \n, \t) aux deux bouts
'Bonjour le monde'
>>> s.split()                      # coupe sur les blancs → liste
['Bonjour', 'le', 'monde']
>>> "a,b,,c".split(",")            # coupe sur un séparateur précis (garde les vides)
['a', 'b', '', 'c']
>>> "-".join(["a", "b", "c"])      # l'inverse : le séparateur est à gauche
'a-b-c'
>>> "hello".upper(), "Hello World".lower(), "hello world".title()
('HELLO', 'hello world', 'Hello World')
>>> "hello".replace("l", "L"), "hello".replace("l", "L", 1)
('heLLo', 'heLlo')
>>> "hello".find("e"), "hello".find("z"), "hello".count("l")
(1, -1, 2)
>>> "hello".startswith("he"), "hello".endswith(".log")
(True, False)
```

Et deux opérateurs : `+` concatène, `*` répète (`"-" * 40` fait une ligne de tirets), `in` teste la présence (`"lo" in "hello"` → `True`). Les comparaisons `<` `>` suivent l'ordre des points de code Unicode, donc `"Z" < "a"` est vrai et `"é" > "z"` aussi : pour trier des mots en français correctement, il faudra `locale` ou une clé de tri (chapitre 4).

### 2.5 Les f-strings

C'est le `printf` de Python, mais les valeurs sont **dans** la chaîne, et ce qui est entre accolades est du Python arbitraire :

```python
>>> x, n = 3.14159, 42
>>> f"{x:.2f}|{n:>10}|{n:<10}|{n:^10}|"
'3.14|        42|42        |    42    |'
>>> f"{n:08b} {n:x} {n:#x} {n:05d} {1234567:,} {0.256:.1%}"
'00101010 2a 0x2a 00042 1,234,567 25.6%'
>>> f"{x=}"                        # debug : le nom et la valeur
'x=3.14159'
>>> f"{{{n}}}"                     # accolades littérales : on les double
'{42}'
```

Après le `:`, c'est le **mini-langage de format** : `[remplissage][alignement][largeur][,][.précision][type]`. Ce qu'il faut connaître :

| Spec | Effet | Équivalent C |
|---|---|---|
| `.2f` | 2 décimales | `%.2f` |
| `>10` `<10` `^10` | aligné à droite/gauche/centré sur 10 | `%10s` `%-10s` |
| `08b` `x` `#x` `o` | binaire sur 8 avec zéros, hexa, hexa préfixé, octal | `%08b` n'existe pas, `%x`, `%#x` |
| `,` `_` | séparateur de milliers | — |
| `e` `g` `%` | scientifique, compact, pourcentage | `%e` `%g` |
| `=` | affiche `nom=valeur` | — |

Tu croiseras aussi l'ancienne forme `"%.2f" % x` (héritée du C, à ne plus écrire) et `"{:.2f}".format(x)` (utile quand le gabarit vient d'un fichier de config). Le f-string couvre tout le reste.

### 2.6 `is` et `==`, en une phrase

`==` compare les **valeurs**, `is` compare les **identités** (est-ce le même objet en mémoire ?). Tu utilises `==` partout, sauf pour `None`, `True`, `False` où l'usage est `is`. Le pourquoi, avec les surprises que ça réserve, est au chapitre 10.

### 2.7 `str` et `bytes`

Voilà le point qui fait le plus souffrir ceux qui viennent du C, où `char *` désigne à la fois du texte et des octets. Python sépare strictement les deux :

- une **`str`** est du texte : une suite de caractères Unicode, sans notion d'octets ni d'encodage ;
- une **`bytes`** est une suite d'entiers de 0 à 255, ce qui sort d'un fichier binaire, d'une socket, d'un `subprocess`.

Passer de l'un à l'autre s'appelle **encoder** (texte → octets) et **décoder** (octets → texte), et il faut préciser l'encodage. Aujourd'hui, c'est UTF-8, point :

```python
>>> "é".encode("utf-8")
b'\xc3\xa9'
>>> "é".encode("latin-1")
b'\xe9'
>>> len("naïve"), len("naïve".encode())
(5, 6)
>>> b"\xc3\xa9".decode("utf-8")
'é'
>>> b"abc"[0]
97
>>> "café".encode("ascii", errors="replace")
b'caf?'
```

Un `é` fait un caractère, mais deux octets en UTF-8 et un seul en Latin-1. `len()` d'une `str` compte les caractères, `len()` d'un `bytes` compte les octets. Indexer un `bytes` renvoie un `int` (le code de l'octet), pas un `bytes` d'un caractère.

> **Piège** : `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9`. C'est un fichier écrit en Latin-1 (Windows d'il y a quinze ans, un vieux export SAP) qu'on lit en UTF-8. La solution n'est pas d'ignorer l'erreur, c'est de lire avec le bon encodage : `open(chemin, encoding="latin-1")` (chapitre 7). Et quand on ne sait pas : `errors="replace"` met un `?` ou un `�` plutôt que de planter, en le disant.

Dans la pratique, la frontière est nette : tout ce qui vient de l'extérieur (fichier, réseau, sortie de commande) arrive en octets ou est décodé à l'entrée, on travaille en `str` à l'intérieur, on encode à la sortie. Les bibliothèques modernes (`open()` en mode texte, `requests`, `subprocess` avec `text=True`) font le décodage pour toi si tu leur donnes l'encodage.

### 2.8 Ce qu'il faut retenir

- Une variable est une étiquette sur un objet ; l'objet a un type, pas l'étiquette.
- `int` illimité, `float` = `double` IEEE 754 avec ses arrondis ; `/` donne un `float`, `//` et `%` arrondissent vers le bas.
- `input()` renvoie une `str`, toujours ; on convertit avec `int()` / `float()`.
- Une `str` est immuable : les méthodes renvoient une nouvelle chaîne. Slicing `[début:fin:pas]`, fin exclue.
- f-string pour tout formatage : `f"{valeur:spec}"`.
- `str` = texte Unicode, `bytes` = octets ; on passe de l'un à l'autre avec `.encode()` / `.decode()` en UTF-8.

**Labo 02** : un convertisseur d'unités en ligne de commande (températures, octets lisibles façon `df -h`, secondes en durée) qui met en pratique conversions, arithmétique entière et f-strings.

---

← [1. Installer, outiller, lancer](01-installer-et-outiller.md) · [Sommaire](../README.md) · [3. Contrôle : conditions et boucles](03-controle-conditions-boucles.md) →
