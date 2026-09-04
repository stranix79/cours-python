# 5. Fonctions

*Python de zéro à FastAPI — chapitre 5 sur 21.* ← [4. Collections : listes, tuples, dicts, sets](04-collections.md) · [Sommaire](../README.md) · [6. Modules, paquets, pip et venv](06-modules-paquets-pip.md) →

> 🧪 Labo associé : [`labs/05-boite-a-outils`](../labs/05-boite-a-outils/README.md)

Tu sais ce qu'est une fonction. Ce chapitre est là pour ce que les fonctions Python ont de différent : elles sont des objets comme les autres, elles acceptent des arguments nommés, elles se souviennent de leur contexte de naissance, et elles cachent un piège célèbre dans leurs valeurs par défaut.

### 5.1 `def` et `return`

```python
def taille_lisible(octets):
    """Convertit un nombre d'octets en texte lisible : 1536 → '1.5 Ko'."""
    for unite in ("o", "Ko", "Mo", "Go", "To"):
        if octets < 1024:
            return f"{octets:.1f} {unite}"
        octets /= 1024
    return f"{octets:.1f} Po"
```

`def` crée la fonction, deux-points, corps indenté. Pas de type de retour, pas de type d'argument, pas d'accolades. La chaîne juste sous le `def` est la **docstring** : elle est stockée dans la fonction (`taille_lisible.__doc__`) et c'est ce que `help(taille_lisible)` affiche. Écris-en une par fonction publique, une ligne suffit.

Trois choses sur `return` :

- une fonction sans `return`, ou avec `return` tout court, renvoie **`None`**. Il n'y a pas de `void` : tout appel a une valeur, quitte à ce que ce soit `None` ;
- on peut renvoyer **plusieurs valeurs** : `return min(v), max(v)` renvoie en réalité *un* tuple, que l'appelant dépaquette avec `lo, hi = minmax(v)` (chapitre 4). C'est le `out` de C# ou le pointeur de sortie du C, en propre ;
- `return` peut apparaître n'importe où, y compris au milieu d'une boucle, comme ci-dessus.

```python
>>> def rien(): pass
>>> print(rien())
None
>>> def minmax(valeurs): return min(valeurs), max(valeurs)
>>> minmax([3, 9, 1])
(1, 9)
>>> lo, hi = minmax([3, 9, 1])
```

> **Venant du C** : pas de prototype à déclarer avant. Mais la fonction doit être *définie* (le `def` exécuté) avant d'être *appelée* : `def` n'est pas une déclaration lue par un compilateur, c'est une instruction exécutée à son tour, qui crée un objet fonction et le range dans une variable. Deux fonctions qui s'appellent mutuellement ne posent pas de problème tant qu'aucune n'est appelée avant que les deux `def` soient passés.

### 5.2 Arguments : positionnels, nommés, par défaut

```python
def connecter(host, port=22, timeout=5, verbose=False):
    ...

connecter("web01")                       # port=22, timeout=5
connecter("web01", 2222)                 # positionnel
connecter("web01", timeout=10)           # nommé : on saute port
connecter(host="web01", verbose=True)    # tout nommé, dans l'ordre qu'on veut
```

Les arguments **nommés** (*keyword arguments*) sont la raison pour laquelle les signatures Python peuvent avoir huit paramètres optionnels sans que ce soit pénible : on ne donne que ce qui change. Lis n'importe quelle doc de bibliothèque, tout est comme ça (`open(fichier, encoding="utf-8")`, `sorted(liste, key=len, reverse=True)`).

Règle : les positionnels d'abord, les nommés ensuite. `connecter(port=22, "web01")` est une erreur de syntaxe.

> **Piège** (le plus célèbre de Python) : **une valeur par défaut est évaluée une seule fois, au `def`, pas à chaque appel.** Avec un défaut immuable (nombre, chaîne, `None`, tuple) c'est sans conséquence. Avec une liste ou un dict, la *même* liste est partagée par tous les appels :
>
> ```python
> >>> def ajouter(x, liste=[]):
> ...     liste.append(x)
> ...     return liste
> >>> ajouter(1)
> [1]
> >>> ajouter(2)
> [1, 2]        # la liste du premier appel a survécu
> ```
>
> L'idiome pour un défaut mutable est `None` et une création dans le corps :
>
> ```python
> def ajouter(x, liste=None):
>     if liste is None:
>         liste = []
>     liste.append(x)
>     return liste
> ```
>
> Ce n'est pas un bug, c'est une conséquence directe du fait que `def` est exécuté une fois et que les variables sont des étiquettes (chapitre 10). Les linters (chapitre 20) te le signaleront.

### 5.3 `*args`, `**kwargs`, `/` et `*`

Une fonction peut accepter un nombre variable d'arguments :

```python
def somme(*nombres):            # nombres est un tuple de tous les positionnels
    return sum(nombres)

def info(**champs):             # champs est un dict de tous les nommés
    for cle, valeur in champs.items():
        print(cle, "=", valeur)

>>> somme(1, 2, 3)
6
>>> info(host="web01", port=22)
host = web01
port = 22
```

Les noms `args` et `kwargs` ne sont qu'une convention ; c'est l'étoile qui compte. Une signature complète se lit dans cet ordre : positionnels, `*args`, nommés avec défaut, `**kwargs`.

```python
>>> def f(a, b, *args, c=0, **kwargs):
...     print(a, b, args, c, kwargs)
>>> f(1, 2, 3, 4, c=5, d=6)
1 2 (3, 4) 5 {'d': 6}
```

L'étoile marche aussi **à l'appel**, pour dépaqueter une séquence ou un dict en arguments :

```python
>>> args = [1, 2]; kw = {"c": 3}
>>> f(*args, **kw)
1 2 () 3 {}
```

C'est l'outil des fonctions qui « passent tout à la suivante » (un wrapper, un décorateur au chapitre 11) : `def wrapper(*args, **kwargs): return f(*args, **kwargs)`.

Deux marqueurs affinent la signature :

- tout ce qui est après `*` seul doit être **nommé** : `def connecter(host, port=22, *, timeout=5)` interdit `connecter("web01", 22, 10)`. Pratique quand un troisième positionnel serait illisible ;
- tout ce qui est avant `/` doit être **positionnel** : `def diviser(a, b, /)` interdit `diviser(a=10, b=4)`. Rare dans ton code, fréquent dans la stdlib (`len(obj, /)`), c'est pour ça que `help()` te le montre.

### 5.4 Portée : la règle LEGB

Où Python cherche un nom qu'il rencontre dans une fonction, dans l'ordre : **L**ocal (la fonction), **E**nclosing (les fonctions qui l'entourent), **G**lobal (le module), **B**uiltin (`len`, `print`, `range`…).

```python
x = 10
def f():
    x = 20          # crée une variable LOCALE x, ne touche pas au x global
    print(x)
f()                 # 20
print(x)            # 10
```

> **Venant du C** : la portée est celle de la **fonction**, pas du bloc. Une variable créée dans un `if` ou un `for` existe encore après. Et il n'y a pas de déclaration : une **affectation** dans une fonction rend le nom local à toute la fonction, même si l'affectation est plus bas que la lecture. `x = x + 1` dans une fonction où `x` est global plante avec `UnboundLocalError`, parce que le `x =` a fait de `x` un nom local, lu avant d'être écrit.

Pour modifier une globale depuis une fonction il faut `global x` ; pour modifier une variable d'une fonction englobante, `nonlocal x`. Le premier est presque toujours un mauvais signe (état caché, tests impossibles) : passe la valeur en argument et renvoie la nouvelle. Le second a un usage légitime, les closures, juste en dessous. Lire une globale ne demande rien : `def f(): print(x)` marche.

### 5.5 Une fonction est un objet

Voilà ce qui change par rapport au C et au Java d'avant les lambdas. Une fonction est une **valeur** : on la range dans une variable, dans une liste, dans un dict, on la passe en argument, on la renvoie.

```python
def ping(host):    return f"ping {host}"
def restart(host): return f"systemctl restart sur {host}"

actions = {"ping": ping, "restart": restart}      # sans parenthèses : l'objet, pas l'appel
commande = "restart"
print(actions[commande]("web01"))                   # systemctl restart sur web01
```

C'est une **table de dispatch** : en C tu ferais un tableau de pointeurs de fonctions, en Java un `switch` ou une `Map<String, Runnable>`. Ici c'est un dict. Toute une famille de `if commande == "ping": ... elif commande == "restart": ...` disparaît.

`ping` sans parenthèses est l'objet, `ping("x")` est l'appel. Un objet fonction a un nom (`ping.__name__`), une doc (`__doc__`), des annotations (`__annotations__`) et un type (`<class 'function'>`).

Passer une fonction en paramètre est le quotidien de la stdlib : `sorted(hosts, key=len)`, `map(str.upper, mots)`, `filter(est_valide, lignes)`, `max(fichiers, key=lambda f: f.stat().st_size)`.

**`lambda`** crée une petite fonction anonyme d'une seule expression, sans `return` :

```python
>>> carre = lambda x: x * x         # équivalent à def carre(x): return x * x
>>> sorted(["web01", "db2", "cache10"], key=len)
['db2', 'web01', 'cache10']
>>> ops = {"+": lambda a, b: a + b, "-": lambda a, b: a - b}
>>> ops["+"](2, 3)
5
```

Si la lambda dépasse une ligne ou si tu la nommes avec `=`, écris un `def` : un `def` a un nom dans les tracebacks, une lambda s'appelle `<lambda>`.

### 5.6 Fonctions imbriquées et closures

On peut définir une fonction dans une fonction. La fonction intérieure voit les variables de l'extérieure (le E de LEGB), et **les garde vivantes** même après que l'extérieure a rendu la main. C'est une **closure** (fermeture).

```python
def multiplicateur(k):
    def mult(x):
        return x * k        # k vient de multiplicateur, et y reste attaché
    return mult

double = multiplicateur(2)
triple = multiplicateur(3)
print(double(5), triple(5))     # 10 15
```

`multiplicateur(2)` est terminée, sa variable locale `k` devrait avoir disparu. Elle vit encore, capturée dans `double.__closure__`. Une closure, c'est une fonction plus l'environnement où elle est née.

Avec `nonlocal`, la closure peut aussi *modifier* cet état :

```python
def compteur():
    n = 0
    def incrementer():
        nonlocal n
        n += 1
        return n
    return incrementer

c = compteur()
print(c(), c(), c())            # 1 2 3
```

> **Venant du C** : un pointeur de fonction n'emporte rien avec lui ; pour lui passer un contexte il faut un `void *user_data` à côté. Une closure, c'est le pointeur et le `user_data` dans le même objet. C'est exactement le mécanisme des **décorateurs** du chapitre 11 : une fonction qui prend une fonction, en fabrique une nouvelle autour, et la renvoie.

### 5.7 Type hints

Depuis Python 3.5 on peut **annoter** les paramètres et le retour :

```python
def taille_lisible(octets: int, decimales: int = 1) -> str: ...
def chercher(hosts: list[str], nom: str) -> str | None: ...
def charger(chemin: str, defaut: dict[str, int] | None = None) -> dict[str, int]: ...
```

Syntaxe : `nom: type`, retour après `->`. `str | None` (3.10+) remplace l'ancien `Optional[str]` ; `list[str]`, `dict[str, int]`, `tuple[int, int]` (3.9+) remplacent `List`, `Dict` du module `typing`. Tu croiseras encore les anciennes formes dans du code de 2020.

> **Piège** : **les annotations ne sont pas vérifiées à l'exécution.** `taille_lisible("abc")` ne plante pas sur l'annotation ; ça plante plus loin, ou pas du tout. Python les stocke (`f.__annotations__`) et les ignore. Ceux qui les lisent : ton éditeur (complétion, erreurs soulignées), `mypy` ou `pyright` (chapitre 20), et des bibliothèques comme FastAPI et pydantic (chapitre 17) qui s'en servent pour valider et documenter. Écris-les : c'est de la doc qui ne ment pas et que les outils comprennent.

### 5.8 Récursion

Ça marche comme partout, avec une limite : la pile d'appels de Python est bornée à 1000 niveaux par défaut (`sys.getrecursionlimit()`), au-delà `RecursionError`. Pas d'optimisation des appels terminaux. Pour parcourir un arbre de fichiers ou un JSON imbriqué, la récursion est naturelle ; pour itérer un million de fois, c'est une boucle.

```python
def factorielle(n: int) -> int:
    return 1 if n <= 1 else n * factorielle(n - 1)

>>> factorielle(20)
2432902008176640000        # int illimité : pas de débordement (chapitre 2)
```

### 5.9 Ce qu'il faut retenir

- `def` est une instruction exécutée qui crée un objet fonction ; sans `return`, une fonction renvoie `None` ; plusieurs valeurs = un tuple.
- Arguments nommés partout ; `*args` et `**kwargs` pour le variable ; `*` et `/` pour contraindre.
- **Jamais de liste ou de dict comme valeur par défaut** : `None` puis création dans le corps.
- Portée LEGB, au niveau de la fonction ; évite `global`.
- Une fonction est une valeur : dict de fonctions = table de dispatch, `key=`, `lambda`, closures.
- Les type hints documentent et outillent, ils ne vérifient rien à l'exécution.

**Labo 05** : une boîte à outils DevOps (tailles lisibles, parsing `clé=valeur`, `retry` qui reçoit une fonction, `slugify`) avec un bloc de démo sous `if __name__ == "__main__":`.

---

← [4. Collections : listes, tuples, dicts, sets](04-collections.md) · [Sommaire](../README.md) · [6. Modules, paquets, pip et venv](06-modules-paquets-pip.md) →
