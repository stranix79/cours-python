# Labo 06 — Mon premier paquet

**Chapitre** : [6. Modules, paquets, pip et venv](../../cours/06-modules-paquets-pip.md)

## Objectif
Transformer la boîte à outils du labo 05 en un vrai paquet Python : plusieurs modules dans un dossier, un `pyproject.toml`, une installation dans le `.venv` et une commande `outils` disponible dans le terminal.

## Consignes
1. Le dossier `outils/` est le paquet. Il contient déjà `__init__.py` (vide pour l'instant) et trois sous-modules à compléter : `texte.py` (`slugify`, `parse_kv`, repris du labo 05), `fichiers.py` (`taille_lisible`, plus une nouvelle `taille_dossier(chemin)` qui additionne la taille de tous les fichiers d'un dossier, récursivement : `pathlib.Path.rglob("*")`), et `reseau.py` (`retry`, plus `port_ouvert(host, port, timeout=1.0)` qui teste une connexion TCP avec `socket.create_connection`). Recopie ton code du labo 05 dans les bons modules.
2. Dans `outils/__init__.py`, ré-exporte les fonctions utiles pour que l'utilisateur puisse écrire `from outils import slugify` sans connaître les sous-modules. Ajoute `__version__ = "0.1.0"`.
3. `outils/cli.py` contient une fonction `main()` qui lit `sys.argv` : `outils slug "Un Texte"`, `outils taille /chemin`, `outils port host 22`. Un dict de dispatch (chapitre 5) fait le lien entre la sous-commande et la fonction. Sans argument, affiche l'usage et sort avec le code 1 (`sys.exit(1)`).
4. Lance-le d'abord sans installer : `python3 -m outils.cli slug "Hello World"`. Puis complète `pyproject.toml` (nom, version, `requires-python`, et la section `[project.scripts]` qui fait pointer la commande `outils` vers `outils.cli:main`).
5. Installe en mode éditable dans le `.venv` : `pip install -e .`. Vérifie que la commande `outils` existe (`which outils`), qu'elle marche depuis n'importe quel dossier, et que modifier `cli.py` change son comportement sans réinstaller (c'est ça, « éditable »). `pip show outils` te dit où il est installé.
6. Bonus : ajoute `[project.optional-dependencies] dev = ["pytest"]` et regarde ce que fait `pip install -e ".[dev]"`. Puis `pip uninstall outils` pour nettoyer.

## Comment lancer
```bash
source ../../.venv/bin/activate
python3 -m outils.cli slug "Serveur Web #1"      # sans installation, depuis ce dossier
pip install -e .                                  # installe TON paquet (celui du dossier courant)
outils slug "Serveur Web #1"                      # depuis n'importe où
outils taille ..                                  # taille du dossier labs/
outils port localhost 22
pip uninstall -y outils                           # nettoyer

# La solution s'installe de la même façon, depuis son dossier :
cd solution && pip install -e . && outils slug "Ça Marche" && pip uninstall -y outils
```

## Pour aller plus loin
- `python3 -c "import outils, sys; print(outils.__file__); print(sys.path)"` après `pip install -e .` : cherche le fichier `.pth` ou le *finder* que pip a déposé dans `.venv/lib/python3.13/site-packages/` pour que ton dossier soit trouvé.
- `pip install build && python3 -m build` fabrique un `dist/outils-0.1.0-py3-none-any.whl` : c'est exactement ce qu'on envoie sur PyPI. Ouvre-le avec `unzip -l`, c'est un zip.
- Remplace `sys.argv` par `argparse` (chapitre 13) : sous-commandes, `--help` gratuit, messages d'erreur propres.
