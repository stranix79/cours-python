# 12. Tester avec pytest

*Python de zéro à FastAPI — chapitre 12 sur 21.* ← [11. Itérateurs, générateurs, décorateurs, `with`](11-iterateurs-generateurs-decorateurs.md) · [Sommaire](../README.md) · [13. Ligne de commande et scripts DevOps](13-ligne-de-commande-et-devops.md) →

> 🧪 Labo associé : [`labs/12-tests`](../labs/12-tests/README.md)

### 12.1 Pourquoi tester, et pourquoi les DevOps ne le font pas

Un script d'infra, on le teste en le lançant. Sur la prod, souvent. Ça marche, jusqu'au jour où on le modifie six mois plus tard pour un cas de plus, et qu'il casse silencieusement les trois cas d'avant. En C, le compilateur attrapait au moins les erreurs de type. En Python, il n'y a pas de compilateur : une faute de frappe dans une branche `else` qu'on n'a jamais exécutée dort là jusqu'au jour où elle sert. **Les tests sont le compilateur de Python.**

Un test, c'est du code qui appelle ton code avec des entrées connues et vérifie la sortie. Trois bénéfices, dans l'ordre où on les découvre :

1. On sait que ça marche *aujourd'hui*, sans lancer à la main.
2. On peut modifier *demain* sans peur : si un test casse, on le voit avant la prod.
3. On écrit mieux : du code testable est du code découpé en fonctions qui prennent des arguments et rendent des valeurs, plutôt qu'un script de 400 lignes qui lit des variables globales et fait des `print`.

Le troisième est le vrai. Les chapitres 13 à 19 supposent que tu écris du code testable.

### 12.2 `assert` et pytest

Python a un mot-clé `assert` : `assert condition, "message"` lève `AssertionError` si la condition est fausse. C'est tout ce qu'il faut pour écrire un test. **pytest** (installé par `requirements.txt`) ajoute la découverte automatique, un rapport lisible, et une trentaine d'outils dont on verra les cinq utiles.

Un module à tester, `calc.py` :

```python
def diviser(a, b):
    if b == 0:
        raise ZeroDivisionError("division par zéro")
    return a / b
```

Ses tests, dans `test_calc.py` à côté :

```python
from calc import diviser

def test_diviser():
    assert diviser(10, 2) == 5

def test_diviser_faux():
    assert diviser(10, 4) == 2       # volontairement faux, pour voir
```

```
$ pytest -q
.F                                                                       [100%]
=================================== FAILURES ===================================
______________________________ test_diviser_faux _______________________________

    def test_diviser_faux():
>       assert diviser(10, 4) == 2
E       assert 2.5 == 2
E        +  where 2.5 = diviser(10, 4)

test_calc.py:9: AssertionError
=========================== short test summary info ============================
FAILED test_calc.py::test_diviser_faux - assert 2.5 == 2
1 failed, 1 passed in 0.04s
```

Les règles de découverte : pytest cherche les fichiers `test_*.py` (ou `*_test.py`), y prend les fonctions `test_*` et les méthodes `test_*` des classes `Test*`. Un test passe s'il ne lève rien. Il échoue sur `AssertionError` ou toute autre exception.

Ce qui rend pytest agréable, c'est l'**introspection de l'assert** : il réécrit le bytecode de tes tests pour te montrer *les valeurs* de chaque côté du `==`, pas seulement « faux ». Pas besoin de `assertEqual(a, b)` : un `assert a == b` suffit, et le rapport dit `2.5 == 2`.

> **Venant de Java** : c'est JUnit, mais sans classe, sans annotation et sans `assertEquals`. Un fichier, des fonctions, des `assert`. La convention de nommage remplace l'annotation `@Test`.

Les options que tu utiliseras tous les jours :

| Option | Effet |
|---|---|
| `-q` / `-v` | moins / plus de détails (`-v` affiche un nom par test) |
| `-x` | s'arrête au premier échec |
| `--lf` | ne relance que les tests qui ont échoué la dernière fois |
| `-k mot` | ne lance que les tests dont le nom contient `mot` |
| `-s` | ne capture pas la sortie (tu vois tes `print`) |
| `--co` | liste les tests sans les lancer |
| `chemin/fichier.py::test_nom` | un seul test |

### 12.3 Organisation

Deux écoles. Pour un script ou un petit outil, les tests **à côté** du code : `outil.py` et `test_outil.py` dans le même dossier. Pour un paquet (chapitre 6), un dossier `tests/` à côté de `src/` :

```
mon-projet/
├── pyproject.toml
├── src/monpaquet/
│   ├── __init__.py
│   └── versions.py
└── tests/
    ├── conftest.py
    └── test_versions.py
```

Le problème classique : `tests/test_versions.py` fait `from monpaquet import versions`, et Python ne trouve pas `monpaquet` parce que `src/` n'est pas dans `sys.path`. Deux solutions propres : installer le paquet en mode éditable (`pip install -e .`, chapitre 20), ou dire à pytest où chercher, dans `pyproject.toml` :

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

`conftest.py` est un fichier spécial : pytest le charge avant les tests du dossier (et des sous-dossiers). On y met les fixtures partagées (12.5) et la configuration. Il n'est jamais importé par ton code.

**La convention des labos de ce cours**, à partir de celui-ci : le test est à la racine du labo, `pytest` le lance contre ton squelette, et `SOLUTION=1 pytest` le lance contre `solution/`. Deux fichiers rendent ça possible, à copier tels quels dans tes projets si le besoin se présente :

```ini
# pytest.ini  (pas de commentaire en fin de ligne dans un .ini : pytest le lirait comme un argument)
[pytest]
addopts = --import-mode=importlib
pythonpath = .
norecursedirs = solution
```

`--import-mode=importlib` : pytest ne touche plus à `sys.path` (sinon il remet le dossier du test en tête et le squelette gagnerait). `pythonpath = .` rend le dossier du labo importable. `norecursedirs = solution` : `pytest` tout court ne descend pas dans `solution/`.

```python
# conftest.py
import os, sys
from pathlib import Path

if os.environ.get("SOLUTION") == "1":
    sys.path.insert(0, str(Path(__file__).parent / "solution"))   # solution/ gagne
```

### 12.4 Paramétrer : un test, dix cas

Le réflexe du débutant est de copier-coller un test en changeant les valeurs. Le décorateur `parametrize` (chapitre 11 : c'est une fonction qui reçoit ta fonction) fait un test par ligne :

```python
import pytest

@pytest.mark.parametrize("a, b, attendu", [
    (10, 2, 5),
    (9, 3, 3),
    (1, 4, 0.25),
])
def test_diviser_param(a, b, attendu):
    assert diviser(a, b) == attendu
```

```
$ pytest -v -k param
test_calc.py::test_diviser_param[10-2-5] PASSED
test_calc.py::test_diviser_param[9-3-3] PASSED
test_calc.py::test_diviser_param[1-4-0.25] PASSED
```

Chaque cas a son nom, échoue indépendamment, et ajouter un cas coûte une ligne. C'est l'outil numéro un pour les parseurs, les convertisseurs, les validateurs : tout ce qui a beaucoup d'entrées possibles.

### 12.5 Fixtures : préparer le terrain

Une **fixture** est une fonction qui prépare quelque chose dont un test a besoin (un fichier temporaire, une connexion, un objet configuré) et le lui passe **par le nom du paramètre**. Tu déclares un paramètre nommé `tmp_path`, pytest voit qu'une fixture s'appelle comme ça, l'exécute, et injecte le résultat.

```python
def lire_config(chemin):
    with open(chemin) as f:
        return dict(l.strip().split("=", 1) for l in f if "=" in l)

def test_lire_config(tmp_path):                  # tmp_path : un dossier temporaire, vide, unique
    fichier = tmp_path / "app.conf"
    fichier.write_text("host=db1\nport=5432\n# commentaire\n")
    assert lire_config(fichier) == {"host": "db1", "port": "5432"}
```

Pas de fichier de test à commiter, pas de nettoyage : `tmp_path` est créé avant, supprimé après (enfin, gardé trois exécutions dans `/tmp/pytest-of-toi/` pour que tu puisses aller voir).

Les fixtures fournies qu'on utilise tout le temps :

| Fixture | Donne |
|---|---|
| `tmp_path` | un `Path` vers un dossier temporaire vide |
| `monkeypatch` | modifier temporairement une variable d'env, un attribut, un `sys.path`… remis en place après |
| `capsys` | capturer ce que le test a écrit sur stdout/stderr |
| `caplog` | capturer les messages `logging` |

```python
def test_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")       # défait automatiquement à la fin du test
    assert os.environ["APP_ENV"] == "test"

def test_affiche(capsys):
    print("bonjour")
    assert capsys.readouterr().out == "bonjour\n"
```

Et les tiennes, avec `@pytest.fixture` :

```python
@pytest.fixture
def config():
    return {"host": "db1", "port": 5432}

def test_config(config):                          # reçoit le dict rendu par la fixture
    assert config["port"] == 5432
```

Une fixture peut avoir une phase « après » : mets un `yield` à la place du `return`, et ce qui suit le `yield` s'exécute après le test. Exactement le `@contextmanager` du chapitre 11.

```python
@pytest.fixture
def connexion_bdd(tmp_path):                      # une fixture peut en utiliser une autre
    conn = sqlite3.connect(tmp_path / "test.db")
    yield conn
    conn.close()                                  # après le test, même s'il a échoué
```

Par défaut une fixture est recréée pour chaque test (`scope="function"`). `scope="module"` ou `scope="session"` la partage : utile pour une base de données qui met deux secondes à démarrer, dangereux si un test la modifie pour le suivant.

### 12.6 Tester qu'une erreur arrive

Le code qui *doit* lever est aussi important que celui qui doit réussir :

```python
def test_division_par_zero():
    with pytest.raises(ZeroDivisionError, match="zéro"):
        diviser(1, 0)
```

Le bloc passe si l'exception attendue est levée dedans, et échoue si rien n'est levé ou si c'est une autre. `match=` est une regex cherchée dans le message : on vérifie que l'erreur explique quelque chose, pas juste qu'elle existe. `pytest.raises` est un gestionnaire de contexte : `__exit__` reçoit l'exception, vérifie son type, et rend `True` pour l'avaler. Chapitre 11, encore.

### 12.7 Mocks : ne pas appeler le réseau

Ton code appelle une API, un `ssh`, un `docker`. Le test ne doit pas : trop lent, pas reproductible, et pas de prod dans les tests. On remplace l'appel par un **mock** : un faux objet qui rend ce qu'on lui dit et enregistre comment il a été appelé.

```python
import urllib.request

def version_distante():
    with urllib.request.urlopen("https://example.invalid/version") as r:
        return r.read().decode().strip()
```

```python
from unittest.mock import patch

def test_version_distante():
    with patch("urllib.request.urlopen") as faux:
        # faux remplace urlopen. On configure ce que rend le with ... as r, puis r.read()
        faux.return_value.__enter__.return_value.read.return_value = b"1.4.2\n"
        assert version_distante() == "1.4.2"
        faux.assert_called_once()
```

`patch("module.nom")` remplace, le temps du bloc, l'attribut `nom` du module par un `MagicMock` : un objet qui accepte n'importe quel attribut, n'importe quel appel, et rend un autre `MagicMock`, sauf là où tu as fixé un `return_value`. À la sortie du `with`, l'original est remis.

> **Piège** : on patche **là où le nom est cherché**, pas là où il est défini. Si `outil.py` fait `from subprocess import run` puis appelle `run(...)`, il faut `patch("outil.run")`, pas `patch("subprocess.run")` : le nom `run` dans `outil` a déjà été copié à l'import. Si `outil.py` fait `import subprocess` et appelle `subprocess.run(...)`, alors `patch("subprocess.run")` marche. C'est la raison pour laquelle, dans du code qu'on veut tester, on préfère `import subprocess` à `from subprocess import run`.

Le plus souvent, `monkeypatch.setattr` suffit et se lit mieux :

```python
def test_ping(monkeypatch):
    def faux_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, returncode=0, stdout="ok", stderr="")
    monkeypatch.setattr(subprocess, "run", faux_run)
    assert ping("db1") is True
```

On le fera au labo 13 pour tester un outil qui lance `ping` sans le lancer.

### 12.8 TDD en pratique

Le *Test-Driven Development* n'est pas une religion, c'est un rythme :

1. **Rouge** : écris un test pour le comportement que tu veux. Lance-le. Il échoue (sinon, ton test ne teste rien).
2. **Vert** : écris le code *minimum* pour qu'il passe. Pas plus.
3. **Refacto** : nettoie le code, en relançant les tests pour vérifier que tu n'as rien cassé.

Ce qu'on y gagne, pour un script d'infra : le test *est* la spécification. « `parse("v1.2.3")` doit donner `1.2.3` » écrit dans un test vaut mieux qu'un commentaire, parce qu'il est vérifié à chaque commit. Et écrire le test d'abord force à concevoir l'appel (quels arguments, quelle valeur de retour) avant d'écrire le corps. C'est le labo 12.

Ce qu'on teste : les fonctions qui **calculent** (parseurs, conversions, décisions). Ce qu'on ne teste pas, ou peu : les `print`, le `main()` qui colle tout ensemble, la bibliothèque standard. Ce qu'on **mocke** : le réseau, le disque hors `tmp_path`, l'horloge, les sous-processus.

**Couverture.** `pip install pytest-cov` puis `pytest --cov=monpaquet --cov-report=term-missing` liste les lignes jamais exécutées par les tests. Un chiffre à 100 % ne prouve rien ; les lignes manquantes disent où regarder.

> **Doctest**, l'autre façon : des exemples dans la docstring, vérifiés par `python3 -m doctest -v module.py`.
> ```python
> def carre(x):
>     """Renvoie x au carré.
>
>     >>> carre(4)
>     16
>     """
>     return x * x
> ```
> Bien pour documenter une fonction pure avec deux exemples. Mal pour tout le reste. pytest sait les lancer aussi : `pytest --doctest-modules`.

> **`unittest`**, la bibliothèque standard : classes `TestCase`, méthodes `setUp`/`tearDown`, `self.assertEqual(a, b)`. C'est du JUnit porté en Python en 2001. Tu le croiseras dans du code ancien ou dans la stdlib elle-même ; pytest lance ces tests sans rien changer, et `unittest.mock` (12.7) reste le module de mock de référence même sous pytest. Pour du code neuf, pytest.

### 12.9 Ce qu'il faut retenir

- Les tests sont le compilateur de Python. Un fichier `test_*.py`, des fonctions `test_*`, des `assert`.
- `parametrize` pour les tables de cas, `pytest.raises` pour les erreurs attendues.
- Les fixtures s'injectent par le nom du paramètre : `tmp_path`, `monkeypatch`, `capsys`, et les tiennes avec `@pytest.fixture` (un `yield` pour la phase après).
- Mocker le réseau, les sous-processus et l'horloge : `monkeypatch.setattr` ou `unittest.mock.patch`, **là où le nom est cherché**.
- Rouge, vert, refacto. `pytest -x --lf` pendant qu'on écrit, `pytest` avant de commiter.
- Dans les labos : `pytest` teste ton code, `SOLUTION=1 pytest` teste la solution.

**Labo 12** : écrire les tests d'un module de versions semver avant le code, cas par cas, puis les faire passer.

---

← [11. Itérateurs, générateurs, décorateurs, `with`](11-iterateurs-generateurs-decorateurs.md) · [Sommaire](../README.md) · [13. Ligne de commande et scripts DevOps](13-ligne-de-commande-et-devops.md) →
