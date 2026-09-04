# Labo 20 — Rendre un paquet prêt à publier

**Chapitre** : [20. Qualité, empaquetage, déploiement](../../cours/20-qualite-empaqueter-deployer.md)

## Objectif
Partir d'un petit paquet `outils` qui marche mais qui est sale (style, imports, annotations fausses, structure à plat) et le rendre publiable : `src/` layout, `pyproject.toml` complet, ruff et mypy sans erreur, tests, wheel construite, Dockerfile, workflow CI.

## Consignes
1. Regarde l'état de départ : `pytest` passe (les tests sont verts), mais `ruff check .` remonte une douzaine d'erreurs et `mypy outils` en trouve d'autres. Note aussi pourquoi `import outils` marche dans les tests : lis `conftest.py`.
2. **Style** : `ruff check . --fix` puis `ruff format .`. Corrige à la main ce qui reste (`E741`, `B006`, `E711`, `E722`…). Chaque règle a une page : `ruff rule B006`.
3. **Types** : `mypy outils` doit passer avec `strict = true`. Il y a des annotations manquantes, une annotation fausse, et un `Optional` mal géré. Ne mets pas de `# type: ignore` : corrige le code.
4. **Structure** : déplace le paquet dans `src/outils/`, complète `pyproject.toml` (build-system hatchling, `[project]` complet, `[project.scripts]` pour la commande `outils`, `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]`). Supprime `conftest.py`, installe en mode développement (`pip install -e ".[dev]"`) et vérifie que `pytest` passe toujours et que `outils --help` répond.
5. **Construire** : `python -m build` doit produire `dist/outils-0.1.0-py3-none-any.whl` et le `.tar.gz`. Ouvre la wheel (`unzip -l`) : qu'est-ce qu'elle contient, et qu'est-ce qu'elle ne contient pas ?
6. **Livrer** : complète le `Dockerfile` (image slim, non-root, dépendances avant le code, `PYTHONUNBUFFERED`) et `.github/workflows/ci.yml` (ruff, mypy, pytest, matrice 3.11 à 3.13). Si Docker est installé : `docker build -t outils . && docker run --rm outils ip 10.0.0.1`.
7. Bonus : refais le point 4 avec `uv` (`uv init`, `uv add --dev ...`, `uv sync`, `uv run pytest`, `uv build`). Compare le `uv.lock` généré avec ce que `pip freeze` te donnait.

## Comment lancer
```bash
source ../../.venv/bin/activate
pytest                     # état de départ : vert
ruff check .               # état de départ : rouge
mypy outils                # état de départ : rouge

cd solution
bash verifier.sh           # ruff + mypy + pytest + build sur la solution
```

Le script `solution/verifier.sh` installe la solution en mode développement dans le `.venv` du cours ; `pip uninstall outils` pour l'enlever ensuite.

## Pour aller plus loin
- `ruff check --select ALL --statistics .` sur la solution : toutes les règles existantes, comptées. Regarde lesquelles tu activerais vraiment et lesquelles sont du bruit.
- `mypy --strict --html-report rapport outils` produit un rapport de couverture des types par fichier.
- Le `.github/workflows/ci.yml` d'un labo n'est pas lu par GitHub (il ne lit que celui de la racine du dépôt) : copie-le à la racine d'un dépôt à toi et regarde-le tourner.
