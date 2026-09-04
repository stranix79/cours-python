# 20. Qualité, empaquetage, déploiement

*Python de zéro à FastAPI — chapitre 20 sur 21.* ← [19. FastAPI avancé : dépendances, auth, tests, Docker](19-fastapi-avance.md) · [Sommaire](../README.md) · [21. Projet final et pour aller plus loin](21-projet-final-et-suite.md) →

> 🧪 Labo associé : [`labs/20-deploiement`](../labs/20-deploiement/README.md)

Jusqu'ici, ton code tourne sur ta machine, dans ton `.venv`, lancé à la main. Ce chapitre est celui qui le fait sortir de là : le rendre lisible par quelqu'un d'autre, vérifié par des outils, installable en une commande, et exécuté par une machine qui n'est pas la tienne. C'est le chapitre le plus DevOps du cours, et probablement celui que tu vas relire le plus.

### 20.1 PEP 8, ou la lisibilité comme convention

Python n'a pas de compilateur qui râle sur le style, mais il a une convention écrite, la [PEP 8](https://peps.python.org/pep-0008/), suivie par à peu près tout le monde. Les règles qui comptent :

| Quoi | Convention | Exemple |
|---|---|---|
| variables, fonctions, modules | `snake_case` | `charger_config`, `delai_ms` |
| classes, exceptions | `CamelCase` | `ClientHttp`, `ErreurConfig` |
| constantes | `UPPER_SNAKE` | `TIMEOUT_DEFAUT = 5` |
| « privé » (convention, pas garantie) | préfixe `_` | `_cache`, `_verifier()` |
| indentation | 4 espaces | jamais de tabulation |
| longueur de ligne | 79 caractères en PEP 8, 88 en pratique | c'est le défaut de black et ruff |
| imports | en haut, un par ligne, triés : stdlib, tiers, locaux | `import os` puis `import httpx` puis `from . import x` |
| espaces | `a = b + c`, `f(x, y=1)`, pas `f( x )` | |

> **Venant de C** : la PEP 8 est à Python ce que le style K&R ou GNU est au C, sauf qu'il n'y en a qu'une. Personne ne discute de la place des accolades, il n'y en a pas. Personne ne discute de `camelCase` contre `snake_case` pour les fonctions, c'est tranché. Ça enlève un sujet de dispute en revue de code.

Tu n'as pas à apprendre la PEP 8 par cœur : un outil la fait respecter à ta place.

### 20.2 ruff : lint et format en un outil

Pendant dix ans, l'outillage Python était un empilement : `flake8` pour les erreurs de style, `isort` pour trier les imports, `black` pour formater, `pyupgrade` pour moderniser la syntaxe, `bandit` pour la sécurité. Depuis 2023, [ruff](https://docs.astral.sh/ruff/), écrit en Rust, fait tout ça, 10 à 100 fois plus vite, avec une seule configuration. Il est dans le `requirements.txt` du cours.

```bash
ruff check .            # lint : signale les problèmes
ruff check . --fix      # corrige ce qui peut l'être sans risque (imports, f-strings…)
ruff format .           # reformate le code (compatible black)
ruff format --check .   # en CI : échoue si un fichier n'est pas formaté
```

Un exemple de ce qu'il attrape, avec les règles `E`, `F` et `I` activées (section suivante) :

```python
# sale.py
import os, sys
import json

def calcule(l):
    resultat = []
    for i in range(len(l)):
        resultat.append(l[i]*2)
    print(os.getcwd(), sys.argv)
    return resultat
```

```
$ ruff check --output-format concise sale.py
sale.py:1:1: E401 [*] Multiple imports on one line
sale.py:1:1: I001 [*] Import block is un-sorted or un-formatted
sale.py:2:8: F401 [*] `json` imported but unused
sale.py:4:13: E741 Ambiguous variable name: `l`
Found 4 errors.
[*] 3 fixable with the `--fix` option.
```

Sans `--output-format concise`, ruff affiche pour chaque erreur l'extrait de code et la correction proposée : plus verbeux, plus pédagogique. L'astérisque `[*]` marque ce que `--fix` corrige tout seul : il sépare les imports, les trie, supprime `json`. Reste `E741`, qui demande un humain : renomme `l` en `valeurs`. Et `for i in range(len(l))` n'est pas une erreur pour ruff, mais c'est du C : `for v in valeurs` est le Python (chapitre 3).

La configuration vit dans `pyproject.toml` (section 20.5). Les règles sont groupées par lettre : `E`/`W` (pycodestyle), `F` (pyflakes : variables non utilisées, imports manquants), `I` (isort), `UP` (pyupgrade : `list[int]` plutôt que `List[int]`), `B` (bugbear : pièges classiques), `SIM` (simplifications), `S` (sécurité). Un bon point de départ :

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]        # la longueur de ligne, c'est le formateur qui s'en occupe
```

Le formateur, lui, n'a pas d'options ou presque. C'est voulu : le formatage n'est plus un sujet, tu lances `ruff format`, c'est fini. Après une semaine, tu ne penses plus jamais à la place d'une virgule.

> **Piège** : `ruff check --fix` supprime un import inutilisé. Si cet import avait un effet de bord (enregistrer un plugin, par exemple), le comportement change. C'est rare, et c'est justement une raison de ne pas écrire d'imports à effet de bord. Dans le doute, `# noqa: F401` sur la ligne.

### 20.3 mypy et pyright : le typage graduel

Les annotations de type (`def f(x: int) -> str`, chapitre 5) ne sont pas vérifiées par Python : à l'exécution, elles sont ignorées. Elles servent à l'éditeur, à la documentation, et à un **vérificateur statique** : [mypy](https://mypy.readthedocs.io/) (historique, dans le `requirements.txt`) ou [pyright](https://github.com/microsoft/pyright) (celui de VS Code via Pylance, plus rapide, plus strict par défaut). Les deux lisent ton code sans le lancer et signalent ce qui ne colle pas.

```python
# verif.py
def delai_total(delais: list[int]) -> int:
    return sum(delais)

delai_total([1, 2, "3"])
```

```
$ mypy verif.py
verif.py:4: error: List item 2 has incompatible type "str"; expected "int"  [list-item]
Found 1 error in 1 file (checked 1 source file)
```

Ce qui est **graduel** : tu peux annoter 10 % de ton code et mypy ne vérifie que ces 10 %. Une fonction sans annotation est traitée comme `Any` partout, ce qui désactive la vérification pour elle. C'est confortable pour commencer et dangereux pour finir : `Any` se propage, et tu crois être vérifié quand tu ne l'es pas. Deux réglages pour resserrer progressivement :

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true           # une fonction annotée qui renvoie un Any : erreur
disallow_untyped_defs = true     # toute fonction doit être annotée
strict = true                    # tout ce qui précède et plus ; l'objectif à terme
```

Passe `strict = true` sur un nouveau projet dès le début : c'est gratuit tant qu'il n'y a pas de code. Sur un projet existant, active les options une par une et corrige module par module.

Trois outils du module `typing` qui reviennent dès qu'on vérifie sérieusement :

| Outil | Sert à | Exemple |
|---|---|---|
| `TypedDict` | typer un dict dont on connaît les clés (config JSON, réponse d'API) | `class Cible(TypedDict): url: str; timeout: int` |
| `Protocol` | typer par comportement, pas par héritage (duck typing vérifié, chapitre 9) | `class Fermable(Protocol): def close(self) -> None: ...` |
| `Generic` / `TypeVar` | une fonction ou classe qui marche pour plusieurs types en gardant le lien entre entrée et sortie | `def premier[T](xs: list[T]) -> T:` (syntaxe 3.12) |

Depuis 3.12, les alias de type ont une syntaxe dédiée : `type Chemin = str | Path` remplace `Chemin = Union[str, Path]`, et les génériques s'écrivent `def f[T](x: T) -> T` sans `TypeVar`. Si tu dois supporter 3.11, garde l'ancienne forme ; sinon, prends la nouvelle.

> **Venant de Java** : c'est ton compilateur qui revient, mais optionnel et à la demande. La différence : `list[int]` ne coûte rien à l'exécution (pas d'*erasure* à contourner, pas de cast), et un `Protocol` te donne des interfaces sans que la classe ait à les déclarer.

### 20.4 pre-commit : lancer tout ça avant que ce soit commité

> **En un encadré** : [pre-commit](https://pre-commit.com) installe un hook git qui lance ruff, mypy et quelques vérifications de base (fin de fichier, YAML valide, pas de gros fichier) à chaque `git commit`. Un `.pre-commit-config.yaml` de dix lignes, `pre-commit install`, et plus personne ne pousse de code non formaté. On ne l'utilise pas dans le cours pour rester simple, mais sur un dépôt d'équipe c'est la première chose à ajouter.

### 20.5 La structure d'un projet et son `pyproject.toml`

Depuis le chapitre 6 tu sais qu'un dossier avec un `__init__.py` est un paquet. Pour en faire un **projet** installable, testable et publiable, voici la structure devenue standard :

```
outils/
├── pyproject.toml          ← tout : métadonnées, dépendances, config des outils
├── README.md
├── LICENSE
├── src/
│   └── outils/             ← le paquet, importé comme `outils`
│       ├── __init__.py
│       ├── dates.py
│       └── reseau.py
└── tests/
    └── test_dates.py
```

Pourquoi `src/` ? Parce qu'avec le paquet directement à la racine, `import outils` marche depuis le dossier du projet *même si le paquet n'est pas installé*, et tes tests passent chez toi alors que l'installation est cassée. Avec `src/`, `import outils` ne marche que si le paquet est installé (`pip install -e .`), donc tu testes ce que l'utilisateur aura. C'est le *src layout* ; la variante sans `src/` (*flat layout*) est tolérée pour les petits projets.

Le `pyproject.toml` remplace `setup.py`, `setup.cfg`, `requirements.txt`, `.flake8`, `mypy.ini` et `pytest.ini`. Un fichier complet :

```toml
[build-system]                        # comment construire le paquet
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]                             # métadonnées (PEP 621)
name = "outils"
version = "0.1.0"
description = "Petits outils dates et réseau"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"
authors = [{ name = "stranix" }]
dependencies = [                      # ce qu'il faut pour que ça tourne
    "httpx>=0.27",
]

[project.optional-dependencies]       # ce qu'il faut pour développer
dev = ["pytest>=8", "ruff>=0.6", "mypy>=1.11"]

[project.scripts]                     # crée une commande `outils` dans le PATH du venv
outils = "outils.cli:main"

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

Trois sections font trois choses différentes, et c'est ce qui trouble au début :

- `[build-system]` dit *quel outil* transforme le dossier en paquet. `hatchling` est le choix moderne et sans surprise ; `setuptools` est l'historique, encore partout.
- `[project]` est **le** standard (PEP 621) : n'importe quel outil (pip, uv, hatch, poetry récent) le lit. `dependencies` remplace `requirements.txt` pour une bibliothèque ; pour une application déployée, on garde en plus un fichier verrouillé avec les versions exactes (section 20.7).
- `[tool.xxx]` : chaque outil y range sa config. Un seul fichier à ouvrir.

Installer le projet en mode développement, c'est à dire lié à ton dossier pour que les modifications soient visibles sans réinstaller :

```bash
pip install -e ".[dev]"     # -e : editable ; [dev] : avec les dépendances optionnelles
outils --help               # la commande définie dans [project.scripts] existe
```

### 20.6 Versionner, construire, publier

**Versionner.** Suis le [semver](https://semver.org) : `MAJEUR.MINEUR.CORRECTIF`. Correctif : un bug réparé, rien ne change pour l'utilisateur. Mineur : une fonctionnalité en plus, compatible. Majeur : quelque chose casse. Une seule source de vérité pour le numéro : le `version` du `pyproject.toml`, que le code peut relire :

```python
# outils/__init__.py
from importlib.metadata import version
__version__ = version("outils")     # lu dans les métadonnées du paquet installé
```

**Construire.** `python -m build` lit `pyproject.toml`, appelle le backend, et produit dans `dist/` deux fichiers :

```
$ python -m build
...
Successfully built outils-0.1.0.tar.gz and outils-0.1.0-py3-none-any.whl
```

Le `.tar.gz` est la **sdist** (source distribution) : tes sources, à construire chez l'utilisateur. Le `.whl` est la **wheel** : un zip prêt à décompresser dans `site-packages`, sans étape de build. `py3-none-any` veut dire « Python 3, pas d'ABI particulière, n'importe quelle architecture » : c'est du Python pur. Une wheel qui contient du C compilé s'appelle plutôt `cp313-cp313-macosx_11_0_arm64.whl`, et c'est pour ça que `pip install numpy` ne compile rien sur ta machine : il télécharge la wheel qui correspond.

**Publier.** [PyPI](https://pypi.org) est le dépôt public ; [TestPyPI](https://test.pypi.org) le bac à sable. Compte, jeton d'API, puis :

```bash
pip install twine
twine upload --repository testpypi dist/*
# ou, avec uv : uv publish --publish-url https://test.pypi.org/legacy/
```

Pour un outil interne, on ne publie pas sur PyPI : on pousse la wheel dans un dépôt privé (Artifactory, Nexus, GitLab Package Registry, ou simplement un dossier servi en HTTP) et on installe avec `pip install --index-url https://…`. Ou on n'empaquète pas du tout, et on livre une image Docker (section 20.8).

### 20.7 uv : le workflow moderne

[uv](https://docs.astral.sh/uv/), par les auteurs de ruff, remplace `venv`, `pip`, `pip-tools`, `pipx`, `pyenv` et une partie de `build`/`twine`, en un binaire Rust, et vite. Depuis 2024 c'est ce qu'il faut regarder pour tout nouveau projet. Le cours a été fait avec `venv` + `pip` pour n'exiger que ce qui est dans la boîte, mais voici l'équivalent :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh    # installation (ou brew install uv)

uv init outils            # crée pyproject.toml, README, .python-version, un hello
cd outils
uv add httpx              # ajoute à [project.dependencies], résout, installe dans .venv
uv add --dev pytest ruff  # dans [dependency-groups] dev
uv sync                   # crée/aligne le .venv sur pyproject.toml et uv.lock
uv run pytest             # lance une commande dans le venv, sans l'activer
uv run outils --help
uv lock                   # régénère uv.lock (fait automatiquement par add/sync)
uv build                  # = python -m build
uv publish                # = twine upload
uv python install 3.13    # télécharge un interpréteur, remplace pyenv
```

Deux idées neuves :

- **`uv.lock`** : la liste exacte de tous les paquets installés, avec versions et empreintes, générée automatiquement. `pyproject.toml` dit « httpx ≥ 0.27 » (ce que ton code exige), `uv.lock` dit « httpx 0.28.1, anyio 4.15.0, … » (ce qui a été testé). On commite les deux. Sur une autre machine, `uv sync` reproduit exactement le même environnement. C'est ce que `requirements.txt` essayait de faire à la main avec `pip freeze`.
- **`uv run`** : plus besoin d'activer le venv. `uv run script.py` s'assure que l'environnement est à jour, puis lance. Dans un `Makefile`, un `Dockerfile` ou un cron, c'est ce qu'on veut.

Et pour les **outils en ligne de commande** que tu veux avoir partout (ruff, pre-commit, httpie…) sans les mettre dans chaque projet : `uv tool install ruff` les installe chacun dans son venv isolé et met la commande dans ton `PATH`. `uvx ruff check .` fait pareil sans même installer. L'ancêtre, [pipx](https://pipx.pypa.io), fait exactement ça et reste très utilisé : `pipx install ruff`.

### 20.8 Docker pour une application Python

Pour une application (une API FastAPI, un worker, un bot), on ne livre pas une wheel : on livre une image. Le `Dockerfile` de référence, commenté :

```dockerfile
# Étape 1 : construire l'environnement avec uv (rapide, reproductible via uv.lock)
FROM python:3.13-slim AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
# D'abord les fichiers de dépendances seuls : cette couche n'est reconstruite
# que si pyproject.toml ou uv.lock change, pas à chaque modification du code.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
# Ensuite le code, et l'installation du projet lui-même.
COPY src/ src/
RUN uv sync --frozen --no-dev

# Étape 2 : l'image finale, sans uv ni cache de build
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"
RUN useradd --create-home --uid 1000 app
WORKDIR /app
COPY --from=build --chown=app:app /app /app
USER app
EXPOSE 8000
CMD ["uvicorn", "outils.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Ce qu'il faut comprendre ligne par ligne :

- **`python:3.13-slim`** : Debian minimale avec Python. Pas `alpine` : musl casse les wheels binaires et tu finis par compiler numpy pendant vingt minutes. Pas l'image complète non plus (1 Go pour rien).
- **Ordre des `COPY`** : Docker met chaque instruction en cache tant que ses entrées n'ont pas changé. Copier `pyproject.toml` + `uv.lock` et installer *avant* de copier le code, c'est ne réinstaller les dépendances que quand elles changent. Sans ça, chaque commit réinstalle tout.
- **Multi-stage** : la première étape a `uv`, les caches, les outils de build. La seconde ne garde que le `.venv` final. Image plus petite, surface d'attaque plus petite.
- **`PYTHONDONTWRITEBYTECODE=1`** : pas de `__pycache__` écrits dans le conteneur (on a déjà compilé avec `UV_COMPILE_BYTECODE`). **`PYTHONUNBUFFERED=1`** : les `print` et logs sortent immédiatement au lieu d'être bufferisés, sinon `docker logs` n'affiche rien jusqu'au crash.
- **`USER app`** : ne jamais tourner en root dans un conteneur. Si l'application est compromise, l'attaquant est `app`, pas `root`.
- **`.dockerignore`** : `.venv`, `.git`, `__pycache__`, `tests`, `*.db`. Sinon ton `.venv` local de 300 Mo part dans le contexte de build.

Sans `uv`, la version classique fonctionne aussi : `COPY requirements.txt`, `RUN pip install --no-cache-dir -r requirements.txt`, `COPY src/`. Le principe des couches est le même.

### 20.9 Intégration continue avec GitHub Actions

Un fichier `.github/workflows/ci.yml` à la racine du dépôt, et chaque push lance lint, typage et tests sur trois versions de Python :

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: ruff check . && ruff format --check .
      - run: mypy src
      - run: pytest
```

La matrice lance le job trois fois en parallèle. Si le paquet dit `requires-python = ">=3.11"`, il faut bien le prouver. Avec uv, remplace les deux premières lignes de `run` par `uses: astral-sh/setup-uv@v5` puis `uv sync --all-extras` et préfixe les commandes de `uv run`.

Un badge dans le README (`![CI](https://github.com/user/repo/actions/workflows/ci.yml/badge.svg)`) et tu sais d'un coup d'œil si `main` est vert.

### 20.10 En production : configuration, secrets, logs

> **Les 12 facteurs, en un encadré** : [12factor.net](https://12factor.net) est une liste de douze principes pour une application déployable, écrite en 2011 chez Heroku et toujours valable. Les trois qui concernent directement ton code Python : **la configuration vient de l'environnement** (pas d'un fichier commité), **les logs vont sur stdout** (c'est la plateforme qui les collecte, pas ton application qui ouvre des fichiers), et **les dépendances sont déclarées explicitement** (`pyproject.toml` + lock, jamais « il faut aussi installer X à la main »).

**Configuration.** Tout ce qui change entre ta machine, la préprod et la prod (URL de base de données, niveau de log, clé d'API) vient de variables d'environnement, lues une fois au démarrage et validées :

```python
# config.py
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    database_url: str
    log_level: str = "INFO"
    timeout_s: int = 5

def charger() -> Config:
    try:
        return Config(
            database_url=os.environ["DATABASE_URL"],        # obligatoire : KeyError sinon
            log_level=os.environ.get("LOG_LEVEL", "INFO"),  # optionnel, avec défaut
            timeout_s=int(os.environ.get("TIMEOUT_S", "5")),
        )
    except KeyError as e:
        raise SystemExit(f"variable d'environnement manquante : {e}") from None
```

Échouer au démarrage avec un message clair vaut mieux que planter deux heures plus tard sur la première requête. Avec FastAPI, `pydantic-settings` fait exactement ça avec validation de type en prime (`class Settings(BaseSettings)`). Pour le développement local, un fichier `.env` (jamais commité, dans `.gitignore`) chargé par `python-dotenv` ou par `uv run --env-file .env`.

**Secrets.** Un secret est une variable d'environnement dont on ne montre jamais la valeur : ni dans le code, ni dans le `Dockerfile` (les `ENV` y sont lisibles avec `docker history`), ni dans les logs. Ils viennent du gestionnaire de secrets de la plateforme (secrets GitHub Actions, Docker secrets, Vault, les Secrets Kubernetes) et sont injectés dans l'environnement au lancement. Si un secret a été commité une fois, considère-le comme public et change-le : `git rm` ne suffit pas, il est dans l'historique.

**Logs.** Le module `logging` du chapitre 8, configuré une fois au démarrage, vers stdout, avec un format qui contient l'heure, le niveau et le module :

```python
import logging, sys
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
```

En conteneur, c'est tout. Docker, systemd, Kubernetes récupèrent stdout et l'envoient où il faut. Pour un pipeline de logs (Loki, Elastic), passe au **JSON structuré** : une ligne par événement, une clé par champ. `python-json-logger` ou `structlog` le font ; le gain est immédiat dès qu'il faut filtrer sur un champ plutôt que grepper une phrase.

### 20.11 Ce qu'il faut retenir

- La PEP 8 n'est pas un sujet : `ruff format` et `ruff check --fix`, et on passe à autre chose.
- Les annotations ne sont vérifiées que par mypy ou pyright ; `strict = true` dès le premier jour d'un nouveau projet.
- Un projet = `pyproject.toml` + `src/paquet/` + `tests/`. Toute la config des outils dans le même fichier.
- `python -m build` produit une wheel (prête à installer) et une sdist (les sources). uv fait tout ça plus vite, avec un `uv.lock` qui rend l'environnement reproductible.
- Une application se livre en image Docker : image slim, dépendances avant le code pour le cache, multi-stage, non-root, `PYTHONUNBUFFERED=1`.
- La CI lance ruff, mypy et pytest sur chaque push. La configuration vient de l'environnement, les logs vont sur stdout, les secrets ne sont jamais dans git.

**Labo 20** : prendre un petit paquet volontairement sale et le rendre prêt à publier : `src/` layout, `pyproject.toml` complet, ruff et mypy sans erreur, tests, wheel construite, Dockerfile et workflow CI.

---

← [19. FastAPI avancé : dépendances, auth, tests, Docker](19-fastapi-avance.md) · [Sommaire](../README.md) · [21. Projet final et pour aller plus loin](21-projet-final-et-suite.md) →
