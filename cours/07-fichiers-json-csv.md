# 7. Fichiers, chemins, JSON, CSV

*Python de zéro à FastAPI — chapitre 7 sur 21.* ← [6. Modules, paquets, pip et venv](06-modules-paquets-pip.md) · [Sommaire](../README.md) · [8. Erreurs, exceptions, logging](08-erreurs-exceptions-logging.md) →

> 🧪 Labo associé : [`labs/07-carnet-adresses`](../labs/07-carnet-adresses/README.md)

La moitié des scripts d'un DevOps lisent un fichier, le transforment et en écrivent un autre. Ce chapitre couvre tout ce qu'il faut pour ça : ouvrir un fichier proprement, manipuler des chemins sans coller des chaînes, et lire ou écrire les trois formats que tu croiseras tous les jours, JSON, CSV et les fichiers de configuration.

### 7.1 `open()` et `with`

```python
with open("hosts.txt", encoding="utf-8") as f:
    for ligne in f:
        nom, ip = ligne.split()
        print(nom, "→", ip)
```

Trois choses dans ces quatre lignes.

**`open()` renvoie un objet fichier.** C'est le `FILE *` du C, avec des méthodes : `f.read()` (tout, en une chaîne), `f.readline()` (une ligne), `f.readlines()` (une liste de lignes), `f.write(texte)`. Mode par défaut : `"r"`, lecture, texte.

**`with` garantit la fermeture.** Le bloc indenté sous `with` est exécuté, puis le fichier est fermé, *quoi qu'il arrive* : fin normale, `return`, exception. C'est l'équivalent d'un `try / finally: f.close()`, en une ligne et sans possibilité d'oublier. En C, un `fopen` sans `fclose` sur un chemin d'erreur, c'est un descripteur qui fuit ; ici c'est structurellement impossible. Le mécanisme derrière (`__enter__`, `__exit__`) s'appelle un *context manager*, on le démonte au chapitre 11. Règle : **on n'écrit jamais `open()` sans `with`**.

**Itérer sur le fichier donne ses lignes**, une par une, sans jamais charger le fichier entier. Pour un log de 4 Go, c'est la différence entre un script qui tourne et un script qui se fait tuer par l'OOM killer. `f.read().split("\n")` charge tout ; `for ligne in f` ne garde qu'une ligne en mémoire. Chaque ligne garde son `\n` final : `ligne.rstrip("\n")` ou `.split()` (qui l'avale) pour s'en débarrasser.

Les modes :

| Mode | Effet |
|---|---|
| `"r"` | lecture (défaut) ; erreur si le fichier n'existe pas |
| `"w"` | écriture ; **écrase** le fichier s'il existe, le crée sinon |
| `"a"` | ajout en fin de fichier (*append*) ; crée si besoin |
| `"x"` | création exclusive ; erreur si le fichier existe |
| `"rb"`, `"wb"` | binaire : on lit et écrit des `bytes`, pas des `str` |
| `"r+"` | lecture et écriture |

```python
with open("journal.log", "a", encoding="utf-8") as f:
    f.write("démarrage\n")          # write n'ajoute pas de \n tout seul
    print("ligne 2", file=f)        # print, si : file= redirige vers le fichier
```

> **Piège** : **mets toujours `encoding="utf-8"`.** Sans lui, Python utilise l'encodage de la locale : UTF-8 sur ton Mac et sur la plupart des Linux, mais cp1252 sur un Windows non configuré, et parfois ASCII dans un conteneur Docker minimal ou un cron sans locale. Le même script marche chez toi et plante en prod sur le premier `é`. Un `encoding` explicite règle le problème pour toujours. (Depuis 3.15, UTF-8 devient le défaut partout ; d'ici là, écris-le.)

### 7.2 Chemins : `pathlib`

Un chemin n'est pas une chaîne. Coller `dossier + "/" + nom` marche jusqu'au jour où `dossier` finit déjà par `/`, ou qu'on est sur Windows. Le module `pathlib` (3.4+) représente un chemin par un objet `Path`, et c'est ce qu'il faut utiliser partout. `os.path` (`os.path.join`, `os.path.exists`…) est l'ancienne API à base de chaînes : tu la croiseras dans du vieux code, tu n'as pas besoin de l'écrire.

```python
from pathlib import Path

conf = Path("/etc") / "nginx" / "nginx.conf"    # l'opérateur / assemble des chemins
conf.name        # 'nginx.conf'
conf.stem        # 'nginx'
conf.suffix      # '.conf'
conf.parent      # PosixPath('/etc/nginx')
conf.parts       # ('/', 'etc', 'nginx', 'nginx.conf')

conf.exists()    # True
conf.is_file(), conf.is_dir()
conf.stat().st_size                 # taille en octets, comme stat(2)

Path.home()      # /Users/stranix
Path.cwd()       # dossier courant
Path(".").resolve()                 # chemin absolu, liens symboliques résolus
```

Les opérations courantes tiennent en une ligne chacune :

```python
p = Path("data") / "machines.json"
p.parent.mkdir(parents=True, exist_ok=True)     # mkdir -p
texte = p.read_text(encoding="utf-8")           # ouvre, lit, ferme
p.write_text(texte, encoding="utf-8")           # ouvre en "w", écrit, ferme
octets = p.read_bytes()

for f in Path("logs").glob("*.log"): ...        # motif, un niveau
for f in Path("logs").rglob("*.log"): ...       # récursif (comme **/*.log)
for f in Path("logs").iterdir(): ...            # tout, un niveau

p.rename("data/old.json")                       # mv
p.unlink(missing_ok=True)                       # rm -f
p.replace("data/final.json")                    # mv qui écrase, atomique sur le même disque
```

`read_text` et `write_text` couvrent 80 % des cas. On sort `open()` quand on veut lire ligne par ligne, écrire en plusieurs fois, ou passer le fichier à `json.load` / `csv.reader`. Et `open()` accepte un `Path` directement.

Pour ce qui dépasse le chemin lui-même, `shutil` : `shutil.copy(src, dst)`, `shutil.copytree`, `shutil.rmtree` (le `rm -rf`, à manier comme tel), `shutil.move`, `shutil.which("docker")` (le `which` du shell), `shutil.disk_usage("/")`. Et `tempfile` pour les fichiers et dossiers temporaires, nettoyés à la sortie du `with` :

```python
import tempfile
with tempfile.TemporaryDirectory() as tmp:      # tmp est une str, le chemin du dossier
    travail = Path(tmp) / "extraction"
    ...
# ici le dossier n'existe plus
```

### 7.3 JSON

JSON est le format d'échange par défaut d'à peu près tout : APIs (chapitre 14 et 17), configs de Docker et de VS Code, sorties de `kubectl -o json`, `terraform show -json`. Le module `json` fait la conversion dans les deux sens entre du texte JSON et des objets Python :

| JSON | Python |
|---|---|
| objet `{}` | `dict` |
| tableau `[]` | `list` |
| chaîne | `str` |
| nombre | `int` ou `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

Quatre fonctions, et c'est tout. `dumps` / `loads` travaillent sur des chaînes (le *s* = string), `dump` / `load` sur des fichiers :

```python
import json

machines = [{"nom": "web01", "ip": "10.0.0.1", "ports": [22, 80], "prod": True, "note": None}]

texte = json.dumps(machines)
# '[{"nom": "web01", "ip": "10.0.0.1", "ports": [22, 80], "prod": true, "note": null}]'
json.loads('{"a": 1, "b": [true, null, 2.5]}')
# {'a': 1, 'b': [True, None, 2.5]}

with open("data/machines.json", "w", encoding="utf-8") as f:
    json.dump(machines, f, indent=2, ensure_ascii=False)
with open("data/machines.json", encoding="utf-8") as f:
    machines = json.load(f)
```

Deux options à connaître : `indent=2` produit du JSON lisible (sinon tout sur une ligne), et `ensure_ascii=False` écrit `"Liège"` au lieu de `"Li\u00e8ge"`. Le défaut `ensure_ascii=True` est un héritage : il garantit un fichier ASCII pur, ce qui n'a plus d'intérêt en 2026.

> **Piège** : JSON ne connaît que les six types du tableau. `json.dumps({"quand": datetime.now()})` lève `TypeError: Object of type datetime is not JSON serializable`. Même chose pour un `set`, un `Path`, un `Decimal`, un objet à toi. Deux issues : convertir avant (`.isoformat()`, `str(path)`, `list(ensemble)`), ou donner à `dumps` une fonction de secours appelée pour tout ce qu'il ne sait pas faire : `json.dumps(donnees, default=str)`. Dans l'autre sens, les clés d'objet JSON sont toujours des chaînes : `{1: "a"}` devient `{"1": "a"}` après un aller-retour.

### 7.4 CSV

Le CSV a l'air simple (des champs séparés par des virgules) et ne l'est pas : virgules dans les valeurs, guillemets, retours à la ligne dans un champ, séparateur `;` dans les exports Excel français. Ne le parse jamais avec `split(",")` ; le module `csv` gère tout ça.

```python
import csv

with open("data/machines.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["nom", "ip", "prod"])
    w.writeheader()
    w.writerow({"nom": "web01", "ip": "10.0.0.1", "prod": True})

with open("data/machines.csv", newline="", encoding="utf-8") as f:
    for ligne in csv.DictReader(f):           # une ligne = un dict, clés = l'en-tête
        print(ligne)                          # {'nom': 'web01', 'ip': '10.0.0.1', 'prod': 'True'}
```

`DictReader` / `DictWriter` travaillent avec des dicts et la ligne d'en-tête ; `reader` / `writer` avec des listes. Pour un CSV à point-virgule : `delimiter=";"`. Le `newline=""` dans le `open()` est obligatoire et documenté : sans lui, sur Windows, chaque ligne est suivie d'une ligne vide.

> **Piège** : **tout ressort en chaîne.** Le `True` écrit est relu comme `'True'`, le `22` comme `'22'`. CSV n'a pas de types ; c'est à toi de convertir (`int(ligne["port"])`). C'est la différence de fond avec JSON, qui sait qu'un nombre est un nombre.

### 7.5 Fichiers de configuration

- **TOML** : le format de `pyproject.toml`, lisible et typé (chaînes, nombres, booléens, dates, listes, tables). Python 3.11 l'inclut en lecture avec `tomllib` ; à noter, il veut le fichier ouvert en **binaire** :

```python
import tomllib
with open("config.toml", "rb") as f:
    cfg = tomllib.load(f)
cfg["serveur"]["port"] + 1          # 8001 : un int, pas une chaîne
```

- **INI** (`[section]` puis `clé = valeur`) : `configparser`, dans la stdlib. Tout est chaîne, avec `getint`, `getboolean` pour convertir. Le format des `.ini`, des `.cfg`, des fichiers de `systemd`, de `git config`.
- **YAML** : le format d'Ansible, Kubernetes, docker-compose, GitHub Actions. Pas dans la stdlib : `pip install pyyaml`, puis `yaml.safe_load(f)`. Toujours `safe_load`, jamais `load` : le `load` historique peut instancier des objets Python arbitraires décrits dans le fichier, ce qui est une exécution de code déguisée. YAML est aussi un superset de JSON, et il a ses propres pièges (`no` est un booléen, `1.10` est un flottant, `022` est de l'octal en YAML 1.1).
- **`.env`** : `CLE=valeur` pour des variables d'environnement. `python-dotenv` les charge ; le plus souvent on préfère lire `os.environ` directement (chapitre 13).

### 7.6 Encodage, `bytes`, fins de ligne

Un fichier ne contient pas des caractères, il contient des **octets**. Un encodage est la table qui fait le lien. En mode texte, Python décode à la lecture et encode à l'écriture avec l'encodage que tu as donné ; en mode binaire (`"rb"`), il te donne les octets bruts, type `bytes`.

```python
>>> Path("latin.txt").write_bytes("Liège".encode("latin-1"))
>>> Path("latin.txt").read_bytes()
b'Li\xe8ge'
>>> Path("latin.txt").read_text(encoding="utf-8")
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe8 in position 2: invalid continuation byte
>>> Path("latin.txt").read_text(encoding="latin-1")
'Liège'
>>> Path("latin.txt").read_text(encoding="utf-8", errors="replace")
'Li�ge'
```

Une `UnicodeDecodeError` veut dire « ce fichier n'est pas dans l'encodage que tu crois ». Un vieux fichier Windows ou un export d'un outil européen des années 2000 est souvent en latin-1 (ISO-8859-1) ou cp1252. `errors="replace"` sauve les meubles pour un log qu'on veut juste lire ; pour des données, trouve le bon encodage (`file fichier.txt` dans le shell aide).

Les fins de ligne : en mode texte, Python convertit les `\r\n` de Windows en `\n` à la lecture (*universal newlines*) et, à l'écriture, écrit le `\n` natif de la plateforme. Tu n'as donc en général rien à faire, sauf pour `csv` (le `newline=""` de plus haut) et pour les fichiers binaires, où rien n'est converti.

### 7.7 Ce qu'il faut retenir

- `with open(chemin, encoding="utf-8") as f:` toujours ; itère sur `f` pour lire ligne par ligne.
- `pathlib.Path` pour tous les chemins : `/` pour assembler, `read_text`, `write_text`, `glob`, `mkdir(parents=True, exist_ok=True)`.
- JSON : `dump`/`load` pour les fichiers, `dumps`/`loads` pour les chaînes ; `indent=2, ensure_ascii=False` ; `default=str` pour ce qui n'est pas sérialisable.
- CSV : le module `csv`, `newline=""`, et tout ressort en chaîne.
- TOML avec `tomllib` (fichier ouvert en `"rb"`), YAML avec `pyyaml` et `safe_load`.
- Un fichier est une suite d'octets ; l'encodage est ce qui en fait du texte.

**Labo 07** : un inventaire de machines persisté en JSON, avec ajout, liste, recherche, suppression, export et import CSV, et une sauvegarde atomique en bonus.

---

← [6. Modules, paquets, pip et venv](06-modules-paquets-pip.md) · [Sommaire](../README.md) · [8. Erreurs, exceptions, logging](08-erreurs-exceptions-logging.md) →
