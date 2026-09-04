# 1. Installer, outiller, lancer

*Python de zéro à FastAPI — chapitre 1 sur 21.* ← [0. Pourquoi Python, et pourquoi maintenant](00-pourquoi-python.md) · [Sommaire](../README.md) · [2. Variables, types, chaînes](02-variables-types-chaines.md) →

> 🧪 Labo associé : [`labs/01-hello`](../labs/01-hello/README.md)

### 1.1 Quel Python ?

Il y a de fortes chances que ta machine ait déjà un Python. Il y a aussi de fortes chances que ce ne soit pas le bon.

```bash
python3 --version
which -a python3        # toutes les versions trouvées dans le PATH, dans l'ordre
```

Ce qu'il te faut : **Python 3.11 ou plus récent**, idéalement 3.13. Oublie Python 2 (mort en 2020) et méfie-toi du Python fourni avec le système (macOS, Debian) : il sert à l'OS, il est souvent vieux, et le modifier peut casser des outils système.

- **macOS** : `brew install python` ou l'installeur de [python.org](https://www.python.org/downloads/). Les deux vont bien.
- **Linux** : `apt install python3 python3-venv python3-pip` (Debian/Ubuntu) ou `dnf install python3` (Fedora). Sur une Debian stable, la version peut être en retard ; ce n'est pas grave pour ce cours tant qu'on a 3.11.
- **Windows** : l'installeur de python.org, en cochant *Add python.exe to PATH*. Ou, mieux pour un DevOps, WSL2 avec une Ubuntu, et on revient au cas Linux.

> **Venant du C** : Python n'a pas de compilateur séparé à installer. L'interpréteur `python3` *est* la chaîne d'outils. Il lit ton `.py`, le compile en bytecode en mémoire, et l'exécute. Le `.pyc` que tu verras apparaître dans des dossiers `__pycache__` est ce bytecode mis en cache : tu peux le supprimer sans rien casser.

### 1.2 Trois façons de lancer du Python

**Le REPL** (Read-Eval-Print Loop). C'est le mode Commodore 64 : tu tapes, il répond.

```
$ python3
Python 3.13.5 (main, Jun 11 2025, 15:36:57) [Clang 17.0.0]
Type "help", "copyright", "credits" or "license" for more information.
>>> 6 * 7
42
>>> nom = "stranix"
>>> f"Bonjour, {nom}"
'Bonjour, stranix'
>>> exit()
```

Tu vas passer beaucoup de temps là-dedans : c'est l'endroit où on vérifie *ce que fait vraiment* une fonction avant de l'écrire dans un script. Trois réflexes à prendre tout de suite :

```python
>>> help(len)          # la doc d'une fonction, q pour quitter
>>> dir("abc")         # tout ce qu'on peut faire avec une chaîne
>>> type(3.14)         # de quel type est cette valeur
<class 'float'>
```

**Un script.** Un fichier texte, extension `.py`, qu'on donne à l'interpréteur :

```bash
python3 hello.py
```

Pas de `main()` obligatoire. L'interpréteur exécute le fichier de haut en bas, comme un script shell. Ce qui n'empêche pas d'en écrire un, et on verra pourquoi au chapitre 6.

**Une ligne, en passant.** Pratique dans un shell ou un pipeline :

```bash
python3 -c "import sys; print(sys.version)"
echo '{"a": 1}' | python3 -m json.tool      # -m lance un module comme un programme
```

Le `-m` va revenir souvent : `python3 -m venv`, `python3 -m pip`, `python3 -m http.server`, `python3 -m pytest`. Ça veut dire « lance ce module de la bibliothèque standard (ou installé) comme s'il était un programme ». L'avantage sur la commande `pip` toute nue, c'est qu'on est sûr d'utiliser le pip *du bon* Python.

### 1.3 L'environnement virtuel, ou pourquoi tu ne fais jamais `pip install` tout nu

Voilà le premier réflexe d'hygiène, et le plus important. Python a un gestionnaire de paquets, `pip`, qui télécharge des bibliothèques depuis [PyPI](https://pypi.org). Par défaut, il les installe dans *le* Python de la machine. Deux projets qui ont besoin de deux versions différentes de la même bibliothèque ? Conflit. Un projet qui a besoin d'une lib, un autre qui n'en veut pas ? Pollution. Et sur Debian ou macOS récent, `pip install` hors environnement est carrément refusé (`externally-managed-environment`).

La solution s'appelle un **environnement virtuel** : un dossier qui contient une copie légère de Python et *ses propres* paquets. Un par projet.

```bash
cd mon-projet
python3 -m venv .venv          # crée le dossier .venv (une fois)
source .venv/bin/activate      # l'active dans ce shell (à chaque session)
                               # Windows cmd : .venv\Scripts\activate.bat
                               # PowerShell : .venv\Scripts\Activate.ps1
(.venv) $ which python         # → mon-projet/.venv/bin/python
(.venv) $ pip install requests # s'installe dans .venv, nulle part ailleurs
(.venv) $ deactivate           # pour en sortir
```

« Activer », c'est juste mettre `.venv/bin` en tête du `PATH` et changer le prompt. Rien de magique : tu peux aussi lancer directement `.venv/bin/python script.py` sans activer, ce qu'on fait souvent dans un `Makefile` ou un `Dockerfile`.

> **Venant de Java** : c'est l'équivalent d'un `pom.xml` avec son `target/` local, ou d'un `node_modules` si tu as touché à Node. Le `.venv` ne se commite jamais ; ce qu'on commite, c'est la liste des paquets (`requirements.txt` ou `pyproject.toml`, chapitre 6).

Le cours a un `requirements.txt` à la racine avec tout ce qu'il faut pour les 22 labos :

```bash
cd cours-python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Pour aller plus vite : `uv`.** Depuis 2024, un outil écrit en Rust, [uv](https://docs.astral.sh/uv/), remplace `venv` + `pip` + `pyenv` en une commande et va dix à cent fois plus vite. Il n'est pas obligatoire pour ce cours (tout marche avec `venv` et `pip`, qui sont dans la boîte), mais si tu commences un projet aujourd'hui, c'est lui qu'il faut regarder. On y revient au chapitre 20.

### 1.4 Un éditeur

N'importe lequel, du moment qu'il connaît Python. **VS Code** avec l'extension *Python* de Microsoft (et *Pylance* qui vient avec) est le choix par défaut : coloration, complétion, erreurs soulignées, débogueur, et il détecte le `.venv` tout seul. **PyCharm** (Community, gratuit) est plus lourd et plus complet. **Vim/Neovim** avec un LSP (`pyright` ou `basedpyright`) si c'est ton monde.

Ce qui compte : que l'éditeur utilise l'interpréteur du `.venv`, sinon il te soulignera en rouge des imports qui marchent très bien. Dans VS Code, en bas à droite, clique sur la version de Python et choisis `.venv/bin/python`.

Deux réglages qui évitent des ennuis : **indentation avec 4 espaces, pas de tabulations** (en Python l'indentation *est* la syntaxe, chapitre 3), et **encodage UTF-8**.

### 1.5 Ton premier script, lu ligne par ligne

```python
# hello.py — premier script : affiche un salut, puis quelques infos sur la machine.
import sys                      # un module de la bibliothèque standard
import platform

nom = "stranix"                 # pas de type, pas de point-virgule
print(f"Bonjour, {nom} !")      # f-string : les {} sont évalués

print("Python", sys.version.split()[0], "sur", platform.system())
```

```
$ python3 hello.py
Bonjour, stranix !
Python 3.13.5 sur Darwin
```

Ce qu'il y a à voir :

- `import sys` charge un module. Tout ce qu'il contient est accessible avec `sys.`. Il n'y a pas de `#include` de fichier d'en-tête et de bibliothèque à lier séparément : le module *est* les deux.
- `print()` est une fonction. En Python 2 c'était une instruction sans parenthèses ; si tu vois `print "x"` quelque part, le code a quinze ans.
- `f"..."` est une chaîne formatée : ce qui est entre accolades est du Python évalué et inséré. C'est le `printf("%s", nom)` du C, en lisible. On en fera le tour au chapitre 2.
- `sys.version.split()[0]` : `sys.version` est une chaîne, `.split()` la coupe en mots (une liste), `[0]` prend le premier. Appels chaînés, lecture de gauche à droite. Tu vas voir ça partout.

### 1.6 Quand ça plante

```
$ python3 hello.py
Traceback (most recent call last):
  File "/Users/stranix/hello.py", line 7, in <module>
    print("Python", sys.versio.split()[0])
                    ^^^^^^^^^^
AttributeError: module 'sys' has no attribute 'versio'. Did you mean: 'version'?
```

Le **traceback** se lit **de bas en haut** : la dernière ligne dit *quoi* (`AttributeError`, avec, depuis 3.10, une suggestion), la ligne au-dessus dit *où* (fichier, numéro de ligne, le code fautif avec des `^` sous l'expression coupable). Quand il y a plusieurs niveaux d'appel, la pile est déroulée du plus ancien (en haut) au plus récent (en bas). C'est l'équivalent d'un `bt` dans gdb, mais gratuit et à chaque erreur.

Pas de segfault, pas de comportement indéfini : une erreur en Python est une **exception**, elle a un nom, un message et une position. On apprendra à les attraper au chapitre 8. Pour l'instant, retiens qu'un traceback n'est pas du bruit, c'est un diagnostic.

### 1.7 Ce qu'il faut retenir

- `python3 --version` : 3.11 minimum, 3.13 recommandé, jamais le Python système pour tes projets.
- Le REPL pour essayer, un script `.py` pour garder, `python3 -m module` pour lancer un outil.
- **Un `.venv` par projet**, toujours. `pip install` seulement dedans.
- Un traceback se lit de bas en haut.

**Labo 01** : installer, créer le `.venv`, écrire et lancer un premier script qui affiche des infos sur ta machine, et provoquer volontairement une erreur pour lire un traceback.

---

← [0. Pourquoi Python, et pourquoi maintenant](00-pourquoi-python.md) · [Sommaire](../README.md) · [2. Variables, types, chaînes](02-variables-types-chaines.md) →
