# Labo 07 — Inventaire de machines

**Chapitre** : [7. Fichiers, chemins, JSON, CSV](../../cours/07-fichiers-json-csv.md)

## Objectif
Un petit outil en ligne de commande qui gère un inventaire de serveurs persisté dans un fichier JSON, avec export et import CSV. Tout ce que tu écriras ici (charger, modifier, sauver) est le squelette de la plupart des scripts d'administration.

## Consignes
1. Complète `charger()` et `sauver()` dans `inventaire.py`. Les données vivent dans `data/inventaire.json`, une liste de dicts `{"nom", "ip", "role", "ports"}`. Si le fichier n'existe pas, `charger()` renvoie une liste vide ; `sauver()` crée le dossier `data/` au besoin (`Path.mkdir(parents=True, exist_ok=True)`) et écrit du JSON indenté, UTF-8, accents lisibles.
2. Complète les commandes : `ajouter nom ip role [ports...]` (refuse un nom déjà présent), `lister` (un tableau aligné : `f"{m['nom']:<10} {m['ip']:<16} {m['role']}"`), `chercher texte` (dans le nom, l'IP ou le rôle, sans tenir compte de la casse), `supprimer nom`.
3. `exporter fichier.csv` : une ligne par machine avec `csv.DictWriter` ; les ports sont joints par `;` dans une seule colonne (`"22;80;443"`).
4. `importer fichier.csv` : lit un CSV avec `csv.DictReader`, reconvertit la colonne ports en liste d'entiers, et ajoute les machines absentes de l'inventaire (par nom). Teste avec `exemple.csv` fourni.
5. Fais un aller-retour complet : ajoute deux machines, exporte, supprime tout (`rm data/inventaire.json`), importe le CSV, liste. Le résultat doit être identique.
6. Bonus : rends `sauver()` **atomique** : écris dans `data/inventaire.json.tmp` puis `Path.replace()` vers le vrai nom. Ainsi un script tué au milieu de l'écriture ne laisse jamais un JSON à moitié écrit. Bonus 2 : une commande `stats` qui compte les machines par rôle avec `collections.Counter`.

## Sortie attendue
```
$ python3 inventaire.py ajouter web01 10.0.0.1 web 22 80 443
web01 ajouté
$ python3 inventaire.py ajouter db01 10.0.0.2 base 22 5432
db01 ajouté
$ python3 inventaire.py lister
nom        ip               rôle       ports
web01      10.0.0.1         web        22, 80, 443
db01       10.0.0.2         base       22, 5432
$ python3 inventaire.py chercher 10.0.0.2
db01       10.0.0.2         base       22, 5432
$ python3 inventaire.py exporter export.csv
2 machine(s) exportée(s) vers export.csv
$ python3 inventaire.py importer exemple.csv
1 machine(s) importée(s), 2 déjà présente(s)
```

## Comment lancer
```bash
source ../../.venv/bin/activate
python3 inventaire.py lister
python3 solution/inventaire.py ajouter web01 10.0.0.1 web 22 80
cat data/inventaire.json                # regarde ce qui a été écrit
rm -rf data export.csv                  # remettre à zéro
```

## Pour aller plus loin
- Remplace les dicts par une `dataclass Machine` (chapitre 9) : `dataclasses.asdict()` pour sérialiser, `Machine(**d)` pour recharger.
- Remplace `sys.argv` par `argparse` (chapitre 13) pour avoir `--help` et des erreurs propres.
- Ajoute un export YAML (`pip install pyyaml`) au format d'un inventaire Ansible, et teste-le avec `ansible-inventory -i inventaire.yml --list` si tu as Ansible.
