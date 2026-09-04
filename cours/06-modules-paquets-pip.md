# 6. Modules, paquets, pip et venv

*Python de zéro à FastAPI — chapitre 6 sur 21.* ← [5. Fonctions](05-fonctions.md) · [Sommaire](../README.md) · [7. Fichiers, chemins, JSON, CSV](07-fichiers-json-csv.md) →

> 🧪 Labo associé : [`labs/06-mon-paquet`](../labs/06-mon-paquet/README.md)

Jusqu'ici tout tenait dans un fichier. Ce chapitre explique comment Python découpe un programme en fichiers, comment il les retrouve, ce que fait vraiment `import`, et comment on installe le code des autres sans casser sa machine.

### 6.1 Un module est un fichier

Un **module**, c'est un fichier `.py`. Rien de plus. `outils.py` est le module `outils`. Pour l'utiliser depuis un autre fichier :

```python
import outils                       # tout le module, accessible par outils.xxx
outils.slugify("Hello World")

from outils import slugify, retry   # juste ces noms, sans préfixe
slugify("Hello World")

import outils as o                  # un alias, courant pour les noms longs
from outils import taille_lisible as tl
```

Ce que fait `import outils` :

1. Python cherche un fichier `outils.py` (ou un dossier `outils/`, section 6.4) dans une liste de dossiers, `sys.path` ;
2. il l'**exécute de haut en bas**, une seule fois. Les `def`, les `class`, les affectations au niveau du fichier s'exécutent, et créent les noms du module ;
3. il range l'objet module obtenu dans le dictionnaire `sys.modules`, sous la clé `"outils"` ;
4. il crée la variable `outils` dans ton fichier, qui pointe vers cet objet.

Le point 2 a deux conséquences qu'il faut avoir en tête. **Un `print()` au niveau du fichier s'exécute à l'import** : c'est pour ça qu'on ne met pas de code de démo en vrac dans un module. Et **un deuxième `import outils`, n'importe où dans le programme, ne réexécute rien** : Python le trouve dans `sys.modules` et rend le même objet. Un module est donc naturellement un *singleton* ; une variable au niveau du module est partagée par tout le programme.

```python
>>> import sys
>>> import json
>>> "json" in sys.modules
True
>>> json.__file__
'/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/json/__init__.py'
>>> import math
>>> math                                    # un module compilé en C
<module 'math' from '.../lib-dynload/math.cpython-313-darwin.so'>
```

> **Venant du C** : `import` n'est pas `#include`. `#include` colle du texte avant compilation ; `import` **exécute** un fichier à l'exécution et te donne un objet. Pas de fichier d'en-tête : le module contient à la fois les déclarations et le code. Et pas d'édition de liens : un module en C compilé (`math`, `_json`, `_sqlite3`) est un `.so` chargé dynamiquement, avec la même syntaxe qu'un module `.py`.

`from outils import *` importe tous les noms publics (ceux qui ne commencent pas par `_`, ou ceux listés dans `__all__`). Ne l'utilise pas en dehors du REPL : on ne sait plus d'où vient quoi.

### 6.2 `if __name__ == "__main__":`

Chaque module a une variable `__name__`. Quand Python **importe** un fichier, `__name__` vaut le nom du module (`"outils"`). Quand Python **lance** un fichier (`python3 outils.py`), le même fichier est chargé sous le nom `"__main__"`.

```python
# outils.py
def slugify(texte): ...

if __name__ == "__main__":
    # exécuté par  python3 outils.py
    # PAS exécuté par  import outils
    print(slugify("Test de la démo"))
```

C'est le `main()` de Python, et la raison pour laquelle un même fichier peut être à la fois une bibliothèque et un programme. Tu verras cet idiome dans presque tous les fichiers de ce cours. L'usage propre, c'est de mettre la logique dans une fonction `main()` et de n'avoir que `main()` sous le `if` : ça permet de l'appeler aussi depuis les tests, ou depuis un `[project.scripts]` (section 6.6).

`python3 -m outils` fait la même chose que `python3 outils.py`, mais en cherchant `outils` dans `sys.path` plutôt qu'un chemin de fichier. C'est ce qui permet `python3 -m json.tool`, `python3 -m http.server`, `python3 -m pytest` : ces modules ont un bloc `__main__` (ou un fichier `__main__.py` pour les paquets).

### 6.3 Comment Python trouve un module : `sys.path`

```python
>>> import sys
>>> sys.path
['', '/Library/Frameworks/Python.framework/Versions/3.13/lib/python313.zip',
 '/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13',
 '.../lib/python3.13/lib-dynload',
 '/Users/stranix/git/cours-python/.venv/lib/python3.13/site-packages']
```

Dans l'ordre : le dossier du script lancé (`''` = le dossier courant dans le REPL), la bibliothèque standard, et `site-packages`, le dossier où pip installe les paquets. Dans un `.venv`, c'est le `site-packages` du `.venv`, et c'est toute l'astuce de l'isolation : activer un venv, c'est changer ce dernier chemin.

Deux conséquences :

- un script trouve les modules **dans son propre dossier**, pas dans le dossier d'où tu le lances. `python3 labs/05/outils.py` trouve les fichiers de `labs/05/` ;
- **piège** : nomme un fichier `json.py` ou `random.py` dans ton projet, et `import json` chargera *le tien* (le dossier du script passe avant la stdlib). Le symptôme classique : `AttributeError: module 'random' has no attribute 'randint'`. Vérifie avec `random.__file__`.

La variable d'environnement `PYTHONPATH` ajoute des dossiers en tête. À réserver au dépannage : la bonne façon de rendre ton code importable de partout, c'est d'en faire un paquet installable (6.6).

### 6.4 Paquets : un dossier de modules

Quand un projet grossit, on range les modules dans un dossier. Un dossier qui contient un fichier `__init__.py` est un **paquet** :

```
outils/
├── __init__.py       ← exécuté par  import outils
├── texte.py          ← import outils.texte
├── fichiers.py
└── cli.py
```

```python
import outils.texte                 # le module texte du paquet outils
outils.texte.slugify("x")

from outils.texte import slugify    # plus courant
from outils import texte
```

`__init__.py` peut être vide (il ne sert alors qu'à marquer le dossier), ou servir de **façade** : y écrire `from .texte import slugify` permet à l'utilisateur d'écrire `from outils import slugify` sans connaître les sous-modules. C'est ce que fait la stdlib (`json` est un paquet, `json.loads` est défini dans `json/decoder.py`) et c'est ce que tu feras dans le labo.

À l'intérieur d'un paquet, deux façons de s'importer entre modules :

```python
from outils.texte import slugify    # import absolu : on nomme le paquet
from .texte import slugify          # import relatif : « texte, à côté de moi »
from ..autre import x               # deux points : le paquet parent
```

Le relatif est plus court et survit à un renommage du paquet, mais il ne marche **que** dans un module importé comme partie d'un paquet. Lancer `python3 outils/cli.py` avec un import relatif dedans plante (`ImportError: attempted relative import with no known parent package`), parce que lancé ainsi, `cli.py` est `__main__` et n'a pas de parent. La solution : `python3 -m outils.cli`, qui charge `cli` comme membre du paquet. Dans le doute, absolu.

> **Venant de Java** : un paquet Python ressemble à un package Java (un dossier = un espace de noms), mais il n'y a pas de règle « une classe publique par fichier ». Un module contient ce qu'on veut : dix fonctions, trois classes, des constantes. On découpe par cohérence, pas par type.

### 6.5 La bibliothèque standard, en une phrase par module

Python est livré « piles incluses ». Avant de chercher sur PyPI, regarde ce qu'il y a déjà. Ceux que tu vas utiliser tout le temps :

| Module | Ce qu'il fait |
|---|---|
| `sys` | l'interpréteur : `argv`, `exit()`, `path`, `stdin/stdout/stderr`, `version` |
| `os` | le système : variables d'environnement (`os.environ`), `getpid()`, `cpu_count()`, permissions |
| `pathlib` | les chemins de fichiers, en objets (chapitre 7) : préfère-le à `os.path` |
| `shutil` | copier, déplacer, supprimer des arbres de fichiers, `which()`, `disk_usage()` |
| `subprocess` | lancer des commandes externes et récupérer leur sortie (chapitre 13) |
| `json`, `csv`, `tomllib` | lire et écrire ces formats (chapitre 7) |
| `datetime`, `time`, `zoneinfo` | dates, durées, horloge, fuseaux |
| `re` | expressions régulières : `re.findall(r"\d+", "eth0 rx 123 tx 456")` → `['0', '123', '456']` |
| `math`, `random`, `statistics`, `decimal`, `fractions` | maths, aléatoire (pas pour la crypto : `secrets`), stats, calcul exact |
| `collections` | `Counter`, `defaultdict`, `deque`, `namedtuple` (chapitre 4) |
| `itertools`, `functools` | outils sur les itérateurs et les fonctions (`partial`, `lru_cache`, chapitre 11) |
| `dataclasses`, `enum`, `typing` | classes de données, énumérations, types (chapitre 9) |
| `logging` | journalisation propre, avec niveaux et destinations (chapitre 8) |
| `argparse` | parser les arguments de ligne de commande (chapitre 13) |
| `urllib.request`, `http.client` | HTTP côté client, sans rien installer (chapitre 14) |
| `http.server`, `socketserver`, `socket` | serveurs minimalistes et sockets brutes (chapitre 16) |
| `sqlite3` | une base SQL complète, dans un fichier (chapitre 18) |
| `asyncio` | l'asynchrone (chapitre 15) |
| `unittest`, `doctest` | tests intégrés (on préférera pytest, chapitre 12) |
| `hashlib`, `hmac`, `secrets`, `base64`, `uuid` | empreintes, secrets, encodages, identifiants |
| `tempfile`, `glob`, `fnmatch` | fichiers temporaires, motifs de noms |
| `pprint`, `textwrap`, `string`, `difflib` | affichage joli, mise en forme de texte, diff |
| `threading`, `multiprocessing`, `concurrent.futures` | parallélisme (chapitre 10 pour le GIL) |

La doc officielle, [docs.python.org/3/library](https://docs.python.org/3/library/), est excellente et existe en français. Réflexe : `python3 -c "import shutil; help(shutil.disk_usage)"`.

### 6.6 pip, requirements.txt et pyproject.toml

Ce qui n'est pas dans la stdlib est sur [PyPI](https://pypi.org) (le *Python Package Index*, 600 000 paquets) et s'installe avec pip, **toujours dans un `.venv` activé** (chapitre 1) :

```bash
pip install requests              # la dernière version
pip install "requests>=2.32,<3"   # une plage de versions
pip install requests==2.32.3      # une version exacte
pip install --upgrade requests
pip uninstall requests
pip list                          # ce qui est installé dans ce venv
pip show requests                 # version, emplacement, dépendances
```

Pour qu'un collègue (ou toi dans six mois, ou un Dockerfile) retrouve le même environnement, on décrit les dépendances dans un fichier. Deux formats coexistent.

**`requirements.txt`** : une liste plate, une ligne par paquet, que `pip install -r requirements.txt` installe. C'est ce que ce cours utilise à la racine. `pip freeze > requirements.txt` génère la liste exacte de tout ce qui est installé, versions épinglées : parfait pour figer une application, trop rigide pour une bibliothèque.

**`pyproject.toml`** : la carte d'identité d'un *projet*, standardisée (PEP 621). Il décrit ton paquet, ses dépendances, ses commandes, et la configuration de tes outils (ruff, mypy, pytest). Le minimum :

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "outils"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["requests>=2.32"]

[project.scripts]
outils = "outils.cli:main"        # crée la commande `outils` → outils/cli.py, fonction main()
```

Avec ce fichier, `pip install .` installe ton paquet dans le venv comme n'importe quel paquet de PyPI, et `pip install -e .` (*editable*) l'installe **en pointant sur ton dossier** : tu modifies le code, c'est pris en compte immédiatement, sans réinstaller. C'est le mode de travail normal sur un projet. Et `[project.scripts]` fabrique un vrai exécutable dans `.venv/bin/`, sans shebang ni `chmod` : c'est ainsi que `pytest`, `uvicorn`, `ruff` arrivent dans ton PATH.

TOML est un format de config simple (`clé = valeur`, sections entre crochets, chaînes entre guillemets, listes entre crochets). Python 3.11 le lit nativement avec `tomllib` (chapitre 7).

### 6.7 Hygiène et sécurité

- **Épingle** les versions de ce que tu déploies (`==` ou une plage étroite) : un `pip install` un an plus tard ne doit pas te donner une version majeure qui a tout changé.
- **Lis le nom deux fois** avant d'installer. Le *typosquatting* existe sur PyPI : `requets`, `python-dateutil` vs `dateutil`, des paquets malveillants qui attendent une faute de frappe. `pip show` te dit qui publie et où est le dépôt.
- Regarde la page PyPI : date de dernière version, nombre de contributeurs, lien vers le code source. Un paquet abandonné depuis 2019 est un risque.
- `pip install` exécute du code du paquet à l'installation (le build). Ce n'est pas un `apt install` signé par une distribution : le niveau de confiance est celui d'un `curl | sh`.
- Ne jamais `sudo pip install`. Jamais.

> **Encadré : uv.** [uv](https://docs.astral.sh/uv/) (Astral, les auteurs de ruff) fait tout ça en une commande et dix fois plus vite : `uv init` crée le `pyproject.toml`, `uv add requests` ajoute la dépendance *et* l'installe dans un `.venv` créé automatiquement, `uv run script.py` lance dans le venv sans l'activer, `uv lock` produit un fichier de verrouillage exact, `uv python install 3.13` télécharge un Python. Tout ce chapitre reste vrai avec uv : il utilise les mêmes `.venv`, `pyproject.toml` et PyPI, il fait juste le travail de `venv` + `pip` + `pyenv` en un seul outil. On y revient au chapitre 20 ; en attendant, `pip` dans un `.venv` suffit et tu comprends ce qui se passe.

### 6.8 Ce qu'il faut retenir

- Un module = un fichier, **exécuté une fois** à l'import, mis en cache dans `sys.modules`.
- `if __name__ == "__main__": main()` : le même fichier sert de bibliothèque et de programme.
- Python cherche dans `sys.path` : dossier du script, stdlib, `site-packages` du venv. Ne nomme pas tes fichiers comme des modules standard.
- Un paquet = un dossier avec `__init__.py` ; imports absolus par défaut ; `python3 -m paquet.module` pour lancer un module d'un paquet.
- Regarde la stdlib avant PyPI.
- `pyproject.toml` + `pip install -e .` : ton code devient un paquet installable avec ses propres commandes.

**Labo 06** : transformer la boîte à outils du labo 05 en paquet `outils/` avec trois sous-modules, une façade dans `__init__.py`, un `pyproject.toml` et une commande `outils` dans le terminal.

---

← [5. Fonctions](05-fonctions.md) · [Sommaire](../README.md) · [7. Fichiers, chemins, JSON, CSV](07-fichiers-json-csv.md) →
