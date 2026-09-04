# 9. Classes et objets

*Python de zéro à FastAPI — chapitre 9 sur 21.* ← [8. Erreurs, exceptions, logging](08-erreurs-exceptions-logging.md) · [Sommaire](../README.md) · [10. Sous le capot : références, mémoire, GIL, bytecode](10-sous-le-capot.md) →

> 🧪 Labo associé : [`labs/09-compte-bancaire`](../labs/09-compte-bancaire/README.md)

### 9.1 Pourquoi des classes

En C, tu as des `struct` d'un côté et des fonctions qui prennent un pointeur vers la struct de l'autre : `serveur_ping(&s)`. Le lien entre les deux n'existe que dans ta tête et dans le préfixe du nom. Une classe, c'est ce lien rendu officiel : les données et les fonctions qui les manipulent vivent ensemble, et `s.ping()` sait tout seul sur quelle struct travailler.

Java pousse ça jusqu'au bout : tout est classe, même `main`, avec `public`, `private`, getters, setters, interfaces, fabriques. Python prend l'idée et jette le cérémonial. Une classe en Python, c'est trois lignes, et tu n'en écris une que quand elle apporte quelque chose : un état qui traîne d'un appel à l'autre, plusieurs fonctions qui partagent les mêmes données, ou un type que tu veux pouvoir comparer, afficher, trier.

Tu utilises déjà des objets depuis le chapitre 2 : `"abc".upper()`, `liste.append(x)`, `chemin.exists()`. Ce chapitre te montre comment ils sont faits.

### 9.2 Une classe, une instance, `self`

```python
class Serveur:
    def __init__(self, nom: str, ip: str):
        self.nom = nom
        self.ip = ip

    def ping(self) -> str:
        return f"ping {self.ip} ({self.nom})"
```

```python
>>> s = Serveur("web-01", "10.0.0.1")
>>> s.ping()
'ping 10.0.0.1 (web-01)'
>>> s.__dict__
{'nom': 'web-01', 'ip': '10.0.0.1'}
```

- `class Serveur:` définit un **type**. `Serveur("web-01", ...)` en crée une **instance** : Python alloue un objet vide puis appelle `__init__` dessus. `__init__` n'est pas un constructeur au sens C++ (l'objet existe déjà quand il tourne), c'est l'**initialiseur**.
- Les attributs ne sont pas déclarés : ils apparaissent quand on les affecte. `self.nom = nom` crée l'attribut `nom` sur *cette* instance. Chaque instance a son propre dictionnaire d'attributs, c'est le `__dict__` ci-dessus.
- **`self`** est le `this` de Java, sauf qu'il est explicite. Une méthode est une fonction ordinaire dont le premier paramètre reçoit l'instance. `s.ping()` est du sucre pour `Serveur.ping(s)`. Les deux écritures marchent. Le nom `self` est une convention, pas un mot-clé, mais ne la casse pas.

> **Venant du C** : `self.nom = nom` ≈ `s->nom = nom`. Et `s.ping()` ≈ `serveur_ping(&s)`, à ceci près que c'est Python qui passe le pointeur.

### 9.3 Attributs d'instance et attributs de classe

Ce qui est affecté sur `self` appartient à l'instance. Ce qui est défini directement dans le corps de la classe appartient à la classe, et est partagé par toutes les instances :

```python
class Compteur:
    total = 0                     # attribut de classe : un seul, partagé

    def __init__(self):
        Compteur.total += 1       # on modifie bien celui de la classe

>>> a, b = Compteur(), Compteur()
>>> Compteur.total, a.total
(2, 2)
```

La lecture `a.total` cherche d'abord dans `a.__dict__`, ne trouve rien, puis dans la classe. C'est pratique pour des constantes ou des valeurs par défaut.

> **Piège** : un attribut de classe **mutable** est partagé par toutes les instances, et elles le modifient toutes ensemble.
> ```python
> class Piege:
>     tags = []                    # UNE liste pour tout le monde
>     def ajouter(self, t):
>         self.tags.append(t)      # lit tags dans la classe, y ajoute
>
> >>> x, y = Piege(), Piege()
> >>> x.ajouter("prod")
> >>> y.tags
> ['prod']                         # y n'a rien demandé
> ```
> C'est le cousin du défaut mutable du chapitre 5. Tout ce qui est propre à une instance se crée dans `__init__` avec `self.tags = []`.

### 9.4 Les méthodes spéciales, ou comment un objet se comporte

Les méthodes dont le nom est entouré de doubles underscores (« dunder ») sont appelées par Python lui-même dans des situations précises. Les définir, c'est brancher ton type sur la syntaxe du langage.

**S'afficher.** `__repr__` est pour le développeur (ce que montre le REPL, les listes, les logs), `__str__` pour l'utilisateur (ce que montre `print`). Écris toujours `__repr__` ; `__str__` seulement si l'affichage humain diffère.

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"     # idéalement : du Python valide

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, autre):
        if not isinstance(autre, Point):
            return NotImplemented                   # « je ne sais pas », pas False
        return (self.x, self.y) == (autre.x, autre.y)
```

```python
>>> p = Point(1, 2)
>>> p
Point(x=1, y=2)
>>> print(p)
(1, 2)
>>> [p]
[Point(x=1, y=2)]
>>> p == Point(1, 2), p == (1, 2)
(True, False)
```

**Se comparer.** Sans `__eq__`, `==` compare les identités (deux instances distinctes ne sont jamais égales, comme deux pointeurs différents). `NotImplemented` renvoyé pour un type inconnu laisse Python essayer l'autre opérande, puis se rabattre sur l'identité. Pour l'ordre, `__lt__` suffit si tu ajoutes `@functools.total_ordering`, qui déduit `<=`, `>`, `>=` :

```python
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, texte: str):
        self.parts = tuple(int(p) for p in texte.split("."))
    def __eq__(self, o): return self.parts == o.parts
    def __lt__(self, o): return self.parts < o.parts
    def __repr__(self): return f"Version({'.'.join(map(str, self.parts))!r})"

>>> Version("2.10.0") > Version("2.9.1")
True
>>> sorted([Version("2.10.0"), Version("1.0.0"), Version("2.9.1")])
[Version('1.0.0'), Version('2.9.1'), Version('2.10.0')]
```

**Se comporter comme une collection.** `len()`, `[]`, `in`, `for` sont branchés sur `__len__`, `__getitem__`, `__contains__`, `__iter__` :

```python
class Pool:
    def __init__(self, hosts):
        self._hosts = list(hosts)
    def __len__(self): return len(self._hosts)
    def __getitem__(self, i): return self._hosts[i]
    def __contains__(self, h): return h in self._hosts
    def __iter__(self): return iter(self._hosts)

>>> pool = Pool(["web-01", "web-02"])
>>> len(pool), pool[0], "web-02" in pool, list(pool)
(2, 'web-01', True, ['web-01', 'web-02'])
```

C'est ça le **duck typing** : Python ne demande pas « es-tu une liste ? », il demande « as-tu `__len__` ? ». Tout objet qui a les bonnes méthodes passe partout où une liste passerait. Pas d'interface à déclarer, pas d'héritage à respecter. Le chapitre 11 en tire les itérateurs et les gestionnaires de contexte.

Autres dunders que tu croiseras : `__hash__` (pour être clé de dict, va avec `__eq__`), `__add__`/`__mul__` (opérateurs), `__call__` (rendre une instance appelable), `__enter__`/`__exit__` (`with`), `__bool__`.

### 9.5 Propriétés : pas de getters ni de setters

En Java on écrit `getCelsius()` et `setCelsius(v)` dès le premier jour, au cas où un jour il faudrait valider. En Python on écrit `t.celsius`, et le jour où il faut valider, on transforme l'attribut en **propriété** sans changer une ligne chez les appelants :

```python
class Temperature:
    def __init__(self, celsius):
        self._c = celsius

    @property
    def celsius(self):                  # lecture : t.celsius
        return self._c

    @celsius.setter
    def celsius(self, v):               # écriture : t.celsius = v
        if v < -273.15:
            raise ValueError("sous le zéro absolu")
        self._c = v

    @property
    def fahrenheit(self):               # calculée, lecture seule
        return self._c * 9 / 5 + 32
```

```python
>>> t = Temperature(20)
>>> t.celsius, t.fahrenheit
(20, 68.0)
>>> t.celsius = -300
ValueError: sous le zéro absolu
>>> t.fahrenheit = 3
AttributeError: property 'fahrenheit' of 'Temperature' object has no setter
```

`@property` est un décorateur (chapitre 11) : il transforme une méthode en attribut calculé. Règle : commence par un attribut nu ; passe à une propriété quand il y a une raison.

### 9.6 `@classmethod`, `@staticmethod`

```python
class Serveur:
    def __init__(self, nom, ip):
        self.nom, self.ip = nom, ip

    @classmethod
    def depuis_ligne(cls, ligne: str) -> "Serveur":
        nom, ip = ligne.split()
        return cls(nom, ip)             # cls = la classe, marche aussi pour les sous-classes

    @staticmethod
    def ip_valide(ip: str) -> bool:
        parts = ip.split(".")
        return len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
```

```python
>>> Serveur.depuis_ligne("web-01 10.0.0.1")
<__main__.Serveur object at 0x...>
>>> Serveur.ip_valide("10.0.0.256")
False
```

- `@classmethod` reçoit la **classe** au lieu de l'instance. Usage principal : des constructeurs alternatifs (`depuis_ligne`, `depuis_dict`, `depuis_json`). Python n'a pas de surcharge de constructeur comme Java ; c'est comme ça qu'on la remplace.
- `@staticmethod` ne reçoit rien : c'est une fonction rangée dans la classe parce qu'elle a un rapport avec elle. Souvent, une fonction de module ferait aussi bien.

### 9.7 Héritage, et pourquoi on en fait moins qu'en Java

```python
class Animal:
    def __init__(self, nom):
        self.nom = nom
    def parler(self):
        return "..."
    def __repr__(self):
        return f"{type(self).__name__}({self.nom!r})"

class Chien(Animal):
    def __init__(self, nom, race):
        super().__init__(nom)           # appelle l'__init__ du parent
        self.race = race
    def parler(self):                   # redéfinition
        return "Wouf"
```

```python
>>> c = Chien("Rex", "berger")
>>> c, c.parler(), isinstance(c, Animal)
(Chien('Rex'), 'Wouf', True)
>>> Chien.__mro__
(<class 'Chien'>, <class 'Animal'>, <class 'object'>)
```

`super()` désigne le parent suivant dans le **MRO** (*method resolution order*), l'ordre dans lequel Python cherche un attribut. Toute classe hérite d'`object` en bout de chaîne. L'héritage multiple existe (`class A(B, C)`), le MRO le rend prévisible, et on le réserve aux *mixins* : de petites classes qui ajoutent une capacité.

Le conseil qui vaut pour tous les langages mais que Python rend facile à suivre : **préfère la composition**. Un `Deploiement` qui *a* un `Serveur` et un `Registre` (attributs) est plus simple à tester et à faire évoluer qu'un `Deploiement` qui *est* un `Serveur`. L'héritage sert quand il y a une vraie relation « est un » et un comportement commun à partager, pas pour réutiliser trois lignes.

### 9.8 Interfaces : `abc` ou `Protocol`

Deux façons de dire « tout objet de ce genre doit savoir faire X ».

**Classe abstraite** (héritage nominal, à la Java) : on hérite explicitement, et Python refuse d'instancier tant que les méthodes abstraites ne sont pas implémentées.

```python
from abc import ABC, abstractmethod

class Stockage(ABC):
    @abstractmethod
    def lire(self, cle): ...
    @abstractmethod
    def ecrire(self, cle, valeur): ...

>>> Stockage()
TypeError: Can't instantiate abstract class Stockage without an implementation for abstract methods 'ecrire', 'lire'
```

**Protocol** (typage structurel, à la duck typing) : on ne hérite de rien. Tout objet qui a les bonnes méthodes *est* conforme, et c'est le vérificateur de types (mypy, Pyright, chapitre 20) qui le contrôle.

```python
from typing import Protocol

class Exportable(Protocol):
    def to_json(self) -> str: ...

class Rapport:                            # n'hérite de rien
    def to_json(self) -> str:
        return '{"ok": true}'

def sauver(obj: Exportable) -> None:      # accepte Rapport, et tout ce qui a to_json
    print(obj.to_json())
```

`Protocol` est la version officielle du duck typing, et c'est celle à préférer pour une API : tu peux rendre conforme une classe d'une bibliothèque que tu ne contrôles pas. `ABC` quand tu veux aussi fournir du code commun aux sous-classes.

### 9.9 Dataclasses : 80 % des classes que tu écriras

Une classe qui sert surtout à transporter des données demande `__init__`, `__repr__`, `__eq__`, parfois `__hash__` et l'ordre. Du code mécanique que `@dataclass` écrit à ta place à partir des annotations :

```python
from dataclasses import dataclass, field

@dataclass
class Hote:
    nom: str
    ip: str
    port: int = 22
    tags: list[str] = field(default_factory=list)   # pas tags = [] : voir 9.3
```

```python
>>> h = Hote("web-01", "10.0.0.1")
>>> h
Hote(nom='web-01', ip='10.0.0.1', port=22, tags=[])
>>> h == Hote("web-01", "10.0.0.1")
True
```

Options utiles : `frozen=True` rend l'instance immuable (et donc hashable, utilisable comme clé de dict ou dans un set), `order=True` génère `<`, `>`… à partir des champs dans l'ordre :

```python
@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int = 0

>>> v = Version(2, 9)
>>> Version(2, 10) > v
True
>>> v.major = 3
FrozenInstanceError: cannot assign to field 'major'
```

`dataclass` refuse un défaut mutable (`tags: list = []` lève `ValueError: mutable default ... use default_factory`) : le piège de 9.3 est bloqué à la source. Tu peux ajouter des méthodes, des propriétés, hériter, comme dans toute classe. Pour de la validation à la construction, il y a `__post_init__`. Pour de la validation *sérieuse* (types, bornes, conversion depuis du JSON), il y a pydantic, que FastAPI utilise partout (chapitre 17).

### 9.10 Visibilité, `Enum`, `__slots__`

**Tout est public.** Pas de `private`. La convention : un underscore devant (`_hosts`) signifie « détail d'implémentation, ne touche pas », et c'est respecté par les outils (pas d'autocomplétion, pas dans `from x import *`) mais pas par l'interpréteur. Deux underscores (`__cache`) déclenchent le *name mangling* : l'attribut est renommé `_Classe__cache` pour éviter les collisions dans les sous-classes. Ce n'est pas de la protection, c'est de l'anti-collision ; on s'en sert rarement.

**`Enum`** pour un ensemble fermé de valeurs nommées, à la place de constantes entières :

```python
from enum import Enum, auto

class Etat(Enum):
    ARRETE = auto()
    DEMARRE = auto()
    ERREUR = auto()

>>> e = Etat.DEMARRE
>>> e, e.name, e.value
(<Etat.DEMARRE: 2>, 'DEMARRE', 2)
>>> Etat["ERREUR"], Etat(1)
(<Etat.ERREUR: 3>, <Etat.ARRETE: 1>)
>>> e is Etat.DEMARRE, e == "DEMARRE"
(True, False)
```

Chaque membre est un singleton : `is` marche, et une chaîne n'est jamais égale à un membre. `StrEnum` (3.11) si tu veux que les membres soient aussi des chaînes (pratique pour du JSON).

**`__slots__`** : `__slots__ = ("x", "y")` dans le corps de la classe supprime le `__dict__` par instance, ce qui divise la mémoire par deux ou trois et interdit d'ajouter des attributs imprévus. Utile pour des millions de petits objets, inutile ailleurs. `@dataclass(slots=True)` le fait pour toi.

### 9.11 Ce qu'il faut retenir

- Une classe regroupe données et fonctions ; `self` est le `this` explicite, une méthode est une fonction dont le premier paramètre est l'instance.
- Les attributs naissent dans `__init__` par affectation. Un attribut de classe mutable est partagé : piège.
- `__repr__` toujours, `__eq__` pour comparer, `__len__`/`__getitem__`/`__iter__` pour se comporter comme une collection : c'est le duck typing.
- Attribut nu d'abord, `@property` quand il faut valider ou calculer. Jamais de getters/setters.
- `@classmethod` pour les constructeurs alternatifs. Composition plutôt qu'héritage ; `Protocol` plutôt qu'`ABC` pour une interface.
- `@dataclass` pour tout ce qui transporte des données : `frozen`, `order`, `default_factory`.

**Labo 09** : un compte bancaire avec héritage, dataclass gelée pour les transactions, exception maison, propriété en lecture seule, constructeur alternatif et un `Protocol`.

---

← [8. Erreurs, exceptions, logging](08-erreurs-exceptions-logging.md) · [Sommaire](../README.md) · [10. Sous le capot : références, mémoire, GIL, bytecode](10-sous-le-capot.md) →
