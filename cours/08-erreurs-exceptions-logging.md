# 8. Erreurs, exceptions, logging

*Python de zéro à FastAPI — chapitre 8 sur 21.* ← [7. Fichiers, chemins, JSON, CSV](07-fichiers-json-csv.md) · [Sommaire](../README.md) · [9. Classes et objets](09-classes-et-objets.md) →

> 🧪 Labo associé : [`labs/08-robuste`](../labs/08-robuste/README.md)

### 8.1 Trois façons de dire « ça a raté »

En C, une fonction qui échoue renvoie `-1` ou `NULL`, et pose `errno`. À toi de tester *chaque* retour. Si tu oublies, le programme continue avec une valeur invalide et plante trois fonctions plus loin, ou pire, ne plante pas. En Java, les *checked exceptions* t'obligent à déclarer `throws IOException` sur toute la chaîne d'appel ou à attraper, ce qui donne des `catch (Exception e) {}` vides écrits pour faire taire le compilateur.

Python a choisi une troisième voie : une erreur est une **exception**, un objet qui remonte la pile d'appels jusqu'à ce que quelqu'un l'attrape. Rien ne t'oblige à l'attraper. Si personne ne le fait, le programme s'arrête avec un traceback. Ce n'est pas un défaut : un script qui plante avec un message clair vaut mieux qu'un script qui continue avec des données fausses.

```python
>>> int("douze")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: invalid literal for int() with base 10: 'douze'
```

`ValueError` est le type, le texte après les deux-points est le message. Une exception porte les deux, plus la pile d'appels au moment où elle a été levée.

> **Venant du C** : une exception est un `longjmp` propre. Elle abandonne les fonctions en cours une par une, en exécutant leurs `finally`, jusqu'à trouver un `except` qui correspond. Aucun code de retour à propager à la main.

### 8.2 try / except / else / finally

```python
def lire(chemin: str) -> str | None:
    try:
        f = open(chemin)             # ce qui peut échouer
    except FileNotFoundError:
        print("absent")              # si ça échoue avec CE type
        return None
    else:
        print("ouvert")              # si ça n'a PAS échoué
        return f.read()
    finally:
        print("finally")             # dans TOUS les cas, même après un return
```

```python
>>> lire("/nope.txt")
absent
finally
```

Quatre blocs, deux qu'on utilise tout le temps (`try`, `except`) et deux qu'on oublie :

- `else` s'exécute seulement si le `try` n'a rien levé. Il sert à sortir du `try` le code qui ne doit *pas* être protégé, pour ne pas masquer ses propres erreurs.
- `finally` s'exécute toujours : nettoyage, fermeture, déverrouillage. Même si un `return` ou une nouvelle exception intervient. C'est l'équivalent du `goto cleanup` en C, en garanti.

On peut avoir plusieurs `except`, testés dans l'ordre, et en grouper avec un tuple :

```python
try:
    port = int(config["port"])
except KeyError:
    port = 8080                              # pas de clé : valeur par défaut
except (ValueError, TypeError) as e:
    raise SystemExit(f"port invalide : {e}") # clé présente mais inutilisable
```

`as e` donne accès à l'objet exception : son message (`str(e)`), ses attributs (`e.errno`, `e.filename` pour les erreurs fichier), sa cause.

### 8.3 La hiérarchie

Toutes les exceptions sont des classes qui héritent les unes des autres. Attraper un parent attrape tous ses enfants.

```
BaseException
├── KeyboardInterrupt        Ctrl-C
├── SystemExit               sys.exit()
└── Exception                ← tout ce que ton code doit attraper hérite d'ici
    ├── ValueError           int("douze"), bonne forme mais mauvaise valeur
    ├── TypeError            1 + "a", mauvais type
    ├── LookupError
    │   ├── KeyError         d["absent"]
    │   └── IndexError       liste[99]
    ├── ArithmeticError
    │   └── ZeroDivisionError
    ├── OSError              tout ce qui vient du système (errno)
    │   ├── FileNotFoundError
    │   ├── PermissionError
    │   └── TimeoutError
    ├── AttributeError       obj.attribut_absent
    ├── ImportError / ModuleNotFoundError
    └── RuntimeError
```

`KeyboardInterrupt` et `SystemExit` héritent de `BaseException` et **pas** de `Exception`, exprès : un `except Exception` ne les avale pas, donc Ctrl-C et `sys.exit()` continuent de marcher à travers ton code.

`OSError` porte `errno` et `strerror`, comme en C, et ses sous-classes sont choisies d'après `errno` : plus besoin de comparer à `ENOENT` toi-même.

```python
>>> try:
...     open("/nope.txt")
... except FileNotFoundError as e:
...     print(e.errno, e.strerror, e.filename)
...
2 No such file or directory /nope.txt
```

> **Piège** : `except:` tout nu (sans type) attrape *tout*, y compris `KeyboardInterrupt` et `SystemExit`. Ton script devient impossible à interrompre. Et `except Exception: pass` avale silencieusement tous les bugs. Les deux sont les erreurs les plus courantes du Python copié-collé. Règle : attrape le type le plus précis que tu sais *traiter*. Ce que tu ne sais pas traiter, laisse remonter.

### 8.4 Lever une exception

```python
def deployer(env: str) -> None:
    if env not in ("dev", "staging", "prod"):
        raise ValueError(f"environnement inconnu : {env!r}")
```

`raise` prend une *instance* d'exception. Les types intégrés couvrent la plupart des besoins ; pour les erreurs propres à ton programme, définis les tiennes. Une classe vide qui hérite d'`Exception` suffit :

```python
class ConfigError(Exception):
    """Fichier de configuration absent, illisible ou incomplet."""
```

Ça permet à l'appelant d'écrire `except ConfigError` sans attraper tous les `ValueError` de la Terre. Et une hiérarchie maison (`class PortInvalide(ConfigError)`) permet d'attraper large ou précis, au choix de l'appelant.

**Chaîner.** Quand tu attrapes une exception de bas niveau pour en lever une de haut niveau, garde la cause avec `from` :

```python
try:
    port = int(brut)
except ValueError as e:
    raise ConfigError("port invalide") from e
```

Le traceback montre alors les deux, reliées par *The above exception was the direct cause of the following exception*. Sans `from`, Python chaîne quand même (*During handling of the above exception, another exception occurred*), mais c'est présenté comme un accident. `from None` coupe la chaîne quand la cause n'apporte rien.

**Relancer.** Dans un `except`, `raise` tout seul relance l'exception en cours, intacte, avec sa pile. Utile pour logger puis laisser remonter :

```python
except OSError:
    log.exception("échec d'écriture")
    raise
```

### 8.5 EAFP : demande pardon, pas permission

Deux façons de lire une clé qui n'existe peut-être pas :

```python
# LBYL : Look Before You Leap (réflexe C)
if "port" in config:
    port = config["port"]
else:
    port = 8080

# EAFP : Easier to Ask Forgiveness than Permission (réflexe Python)
try:
    port = config["port"]
except KeyError:
    port = 8080
```

Python préfère la seconde, et pas seulement par goût. Le test préalable a une **course** : entre `os.path.exists(f)` et `open(f)`, le fichier peut disparaître. Le `try` n'a pas ce problème. Et le chemin normal est plus rapide : un `try` qui ne lève rien ne coûte presque rien, alors que le `if` est payé à chaque fois.

Pour ce cas précis il y a `config.get("port", 8080)`, mais l'idée reste : quand l'échec est *possible mais rare*, tente et attrape.

### 8.6 Lire et manipuler un traceback

Le traceback qui s'affiche quand rien n'attrape est produit par le module `traceback`. Tu peux t'en servir toi-même :

```python
import traceback

try:
    1 / 0
except ZeroDivisionError:
    texte = traceback.format_exc()     # le traceback complet, en chaîne
    print(texte.splitlines()[-1])      # → ZeroDivisionError: division by zero
```

Un `except` qui affiche seulement `str(e)` perd la pile, et donc l'endroit du bug. Garde `format_exc()` (ou `log.exception`, section 8.8) quand tu enregistres une erreur inattendue.

Depuis 3.11, plusieurs exceptions peuvent voyager ensemble dans un `ExceptionGroup`, attrapé avec `except*` ; tu le croiseras en asynchrone (chapitre 15), pas avant.

### 8.7 `assert` n'est pas une vérification

```python
assert x >= 0, "x doit être positif"
```

lève `AssertionError` si la condition est fausse. Mais `python3 -O` **supprime tous les `assert`** à la compilation. Donc : `assert` pour documenter une invariante que tu crois vraie (« ici, la liste est triée »), jamais pour valider une entrée utilisateur, un fichier ou un argument. Pour ça, un `if` et un `raise ValueError`.

### 8.8 Logging : pourquoi pas `print`

`print` va sur stdout, sans date, sans niveau, sans savoir de quel module il vient, et impossible à couper sans éditer le code. Un script d'infra qui tourne dans un cron, un conteneur ou un pipeline a besoin de mieux. Le module `logging` de la bibliothèque standard fait ça, et il est utilisé par toutes les bibliothèques que tu vas croiser : quand tu le configures, tu configures aussi leurs messages.

Quatre pièces :

| Pièce | Rôle |
|---|---|
| **Logger** | l'objet à qui tu parles : `log.info("...")`. Un par module, nommé d'après lui. |
| **Niveau** | `DEBUG` < `INFO` < `WARNING` < `ERROR` < `CRITICAL`. En dessous du seuil, le message est jeté. |
| **Handler** | où ça part : console (`StreamHandler`), fichier (`FileHandler`, `RotatingFileHandler`), syslog, HTTP… |
| **Formatter** | la mise en forme : date, niveau, nom, message. |

Le minimum, à mettre **une seule fois, dans le script principal** :

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

log.debug("détail invisible au niveau INFO")
log.info("démarrage")
log.warning("disque à 91 %")
try:
    1 / 0
except ZeroDivisionError:
    log.exception("calcul impossible")     # = log.error + le traceback
```

```
2026-09-04 13:52:01,681 INFO     __main__: démarrage
2026-09-04 13:52:01,681 WARNING  __main__: disque à 91 %
2026-09-04 13:52:01,681 ERROR    __main__: calcul impossible
Traceback (most recent call last):
  File "b.py", line 11, in <module>
    1 / 0
    ~^~
ZeroDivisionError: division by zero
```

Ce qu'il faut voir :

- `getLogger(__name__)` : dans un module importé, `__name__` vaut son nom (`monpaquet.config`), donc chaque ligne dit d'où elle vient. Dans le script lancé directement, c'est `__main__` (chapitre 6).
- Le format est du vieux style `%(...)s` : c'est le seul endroit où tu le rencontreras encore, `logging` étant antérieur aux f-strings.
- `log.exception(...)` s'utilise dans un `except` : il ajoute le traceback complet. C'est *ça* qu'il faut mettre à la place de `print(e)`.
- Par défaut, `basicConfig` écrit sur **stderr**, pas stdout. Ton script peut donc produire des données sur stdout (à piper) et des logs sur stderr, sans mélange.

**Console et fichier à deux niveaux différents.** Le cas classique : l'utilisateur voit `INFO` et plus, le fichier garde tout pour le diagnostic.

```python
import logging

racine = logging.getLogger()               # le logger racine, parent de tous
racine.setLevel(logging.DEBUG)             # laisse tout passer ; les handlers filtrent

console = logging.StreamHandler()          # stderr
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

fichier = logging.FileHandler("deploiement.log", encoding="utf-8")
fichier.setLevel(logging.DEBUG)
fichier.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)-8s %(name)s %(funcName)s:%(lineno)d %(message)s"))

racine.addHandler(console)
racine.addHandler(fichier)
```

Le niveau du logger est le premier filtre, celui de chaque handler le second. D'où le `DEBUG` sur la racine : sinon rien ne passerait au fichier.

**Ce qu'on ne logge pas** : mots de passe, jetons, clés d'API, contenu de cartes. Un fichier de log est copié, archivé, envoyé au support, indexé. Si une valeur est secrète, logge sa présence (`"token: fourni"`), sa longueur, ses quatre derniers caractères, jamais la valeur.

### 8.9 Ce qu'il faut retenir

- Une erreur est un objet qui remonte la pile ; si personne ne l'attrape, le programme s'arrête proprement avec un traceback. C'est un diagnostic, pas un échec.
- Attrape **précis** et seulement ce que tu sais traiter. Jamais `except:` nu, jamais `except Exception: pass`.
- `finally` pour nettoyer, `else` pour le code qui ne doit pas être protégé, `raise ... from e` pour chaîner, `raise` seul pour relancer.
- Tes propres exceptions : une classe vide héritant d'`Exception`.
- EAFP : tente, attrape. `assert` disparaît avec `-O`, jamais pour valider une entrée.
- `logging`, pas `print` : `basicConfig` une fois dans le script principal, `getLogger(__name__)` partout, `log.exception` dans les `except`. Jamais de secret dans un log.

**Labo 08** : rendre robuste un script de déploiement qui lit un `config.json` et un fichier de hosts, avec exception maison, logging console + fichier, et codes de sortie corrects pour le shell.

---

← [7. Fichiers, chemins, JSON, CSV](07-fichiers-json-csv.md) · [Sommaire](../README.md) · [9. Classes et objets](09-classes-et-objets.md) →
