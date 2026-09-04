# 13. Ligne de commande et scripts DevOps

*Python de zéro à FastAPI — chapitre 13 sur 21.* ← [12. Tester avec pytest](12-tests-pytest.md) · [Sommaire](../README.md) · [14. HTTP et APIs, côté client](14-http-et-apis-cote-client.md) →

> 🧪 Labo associé : [`labs/13-cli-devops`](../labs/13-cli-devops/README.md)

Ce que tu vas écrire le plus souvent en Python, ce n'est pas une API : c'est un outil en ligne de commande. Un script qui remplace vingt lignes de bash devenues illisibles, qui interroge trois serveurs, qui parse une sortie de `docker` ou de `kubectl`, qui bouge des fichiers. Ce chapitre est la boîte à outils de ce quotidien, et une façon de structurer ces scripts pour qu'ils restent testables.

### 13.1 Les arguments : `sys.argv`, `argparse`, `typer`

`sys.argv` est la liste des arguments, `argv[0]` étant le nom du script, comme en C. Ça suffit pour un script à un argument. Dès qu'il y a une option, on prend **argparse** (bibliothèque standard) :

```python
import argparse
import sys

def main(argv=None):
    parser = argparse.ArgumentParser(prog="outil", description="Gère des serveurs.")
    parser.add_argument("-v", "--verbose", action="store_true", help="plus de détails")
    sous = parser.add_subparsers(dest="commande", required=True)

    p_ping = sous.add_parser("ping", help="teste un hôte")
    p_ping.add_argument("hote")                                   # positionnel, obligatoire
    p_ping.add_argument("--timeout", type=float, default=2.0,     # converti en float
                        help="secondes (défaut : %(default)s)")

    p_list = sous.add_parser("list", help="liste l'inventaire")
    p_list.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)     # None → sys.argv[1:] ; une liste → testable
    print(args)
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

```
$ python3 outil.py ping db1 --timeout 0.5
Namespace(verbose=False, commande='ping', hote='db1', timeout=0.5)
$ python3 outil.py ping
usage: outil ping [-h] [--timeout TIMEOUT] hote
outil ping: error: the following arguments are required: hote
$ python3 outil.py --help
usage: outil [-h] [-v] {ping,list} ...
...
```

Ce que tu gagnes pour ces quinze lignes : `--help` généré, les erreurs d'usage avec le code de sortie 2, les conversions de type, les sous-commandes à la `git`. Un détail qui compte pour les tests : `parse_args(argv)` accepte une liste, donc `main(["ping", "db1"])` s'appelle depuis pytest sans toucher à `sys.argv`.

> **Venant du C** : `getopt` te faisait écrire la boucle et le `switch` à la main. argparse est déclaratif : tu décris les options, il parse et il documente.

**typer** (installé par `requirements.txt`) va plus loin : les arguments sont déduits de la **signature** et des **type hints** de tes fonctions. Chaque fonction décorée est une sous-commande, sa docstring devient l'aide, ses paramètres deviennent options ou positionnels selon qu'ils ont une valeur par défaut :

```python
import typer

app = typer.Typer(help="Gère des serveurs.")

@app.command()
def ping(hote: str, timeout: float = 2.0):
    """Teste un hôte."""
    print(f"ping {hote} (timeout {timeout}s)")

@app.command("list")                                    # nom explicite : list est un builtin
def lister(json_: bool = typer.Option(False, "--json")):
    """Liste l'inventaire."""
    print("json" if json_ else "tableau")

if __name__ == "__main__":
    app()
```

```
$ python3 outil_typer.py ping db1 --timeout 0.5
ping db1 (timeout 0.5s)
$ python3 outil_typer.py --help
 Usage: outil_typer.py [OPTIONS] COMMAND [ARGS]...
 Gère des serveurs.
╭─ Commands ────────────────────────────────╮
│ ping  Teste un hôte.                      │
│ list  Liste l'inventaire.                 │
╰───────────────────────────────────────────╯
```

typer est construit sur `click` et affiche avec **rich** : couleurs, tableaux, barres de progression dans le terminal, qui disparaissent proprement quand la sortie est redirigée. Pour un outil que d'autres vont utiliser, typer. Pour un script jetable ou sans dépendance, argparse. Le labo 13 est en typer.

### 13.2 Codes de sortie, stdout, stderr, pipes

Un outil en ligne de commande a un contrat avec le shell, le même qu'en C :

- **code de sortie** : 0 si tout va bien, autre chose sinon. `sys.exit(1)` ; `sys.exit("message")` affiche le message sur stderr et sort avec 1. Une exception non attrapée sort avec 1 et un traceback. argparse sort avec 2 sur une erreur d'usage. Sans ça, `outil && deploy` ou `set -e` dans un script shell ne veulent rien dire.
- **stdout** pour le résultat, **stderr** pour le reste (progression, avertissements, erreurs). `print(..., file=sys.stderr)`. Celui qui fait `outil list --json | jq` ne veut pas ton « Connexion en cours… » dans son JSON.
- **stdin** quand on ne donne pas de fichier : `sys.stdin` est un fichier comme un autre, itérable ligne par ligne. Un outil qui lit un fichier *ou* stdin s'enchaîne avec `grep`.

```python
import sys

def lire_source(chemin: str | None):
    if chemin is None or chemin == "-":
        return sys.stdin                    # cat log | outil
    return open(chemin)                     # outil log

if sys.stdout.isatty():
    print("\033[32mOK\033[0m")              # couleurs seulement pour un humain
else:
    print("OK")                             # pas d'échappements ANSI dans un pipe ou un fichier
```

`isatty()` dit si la sortie est un terminal. rich fait ce test tout seul. Une option `--json` qui sort du JSON brut sur stdout est le meilleur cadeau que tu puisses faire à ton toi du futur qui devra brancher l'outil sur autre chose.

### 13.3 Variables d'environnement

`os.environ` est un dict : `os.environ["HOME"]`, ou `os.environ.get("NEXISTE", "défaut")` pour ne pas planter sur une clé absente. Les modifier ne change que ton processus et ses enfants, comme en C. C'est la façon normale de passer une configuration ou un secret à un outil ou un conteneur : `DATABASE_URL`, `API_TOKEN`, `LOG_LEVEL`.

> **`python-dotenv`** (`pip install python-dotenv`, non inclus dans le cours) lit un fichier `.env` (`CLE=valeur` par ligne) et le charge dans `os.environ` avec `load_dotenv()`. Pratique en développement, le `.env` va dans `.gitignore`. En production, les variables viennent de Docker, systemd ou du gestionnaire de secrets.

### 13.4 Lancer des commandes : `subprocess`

Le module pour lancer `git`, `docker`, `ssh`, `kubectl`, `ping`, et récupérer ce qu'ils disent. Une seule fonction à connaître, `subprocess.run` :

```python
import subprocess

r = subprocess.run(["git", "--version"], capture_output=True, text=True)
```

```python
>>> r.returncode, r.stdout.strip(), r.stderr
(0, 'git version 2.50.1 (Apple Git-155)', '')
```

Les arguments qui comptent :

| Argument | Effet |
|---|---|
| `["cmd", "arg1", "arg2"]` | la commande **en liste**, un élément par argument, jamais une chaîne (voir piège) |
| `capture_output=True` | récupère stdout et stderr dans le résultat au lieu de les laisser filer au terminal |
| `text=True` | des `str` au lieu de `bytes` (décodés en UTF-8) |
| `check=True` | lève `CalledProcessError` si le code de sortie n'est pas 0 |
| `timeout=5` | lève `TimeoutExpired` au-delà, et tue le processus |
| `cwd=`, `env=` | dossier de travail, variables d'environnement de l'enfant |
| `input="..."` | ce qu'on envoie sur son stdin |

```python
try:
    subprocess.run(["ls", "/nexiste/pas"], capture_output=True, text=True, check=True)
except subprocess.CalledProcessError as e:
    print("échec", e.returncode, e.stderr)      # échec 1 ls: /nexiste/pas: No such file or directory

try:
    subprocess.run(["sleep", "5"], timeout=0.2)
except subprocess.TimeoutExpired:
    print("trop long")
```

> **Piège** : `subprocess.run("ls " + dossier, shell=True)`. Avec `shell=True`, la chaîne est donnée à `/bin/sh`, et si `dossier` vaut `"; rm -rf /"`, tu viens d'écrire une injection de commande. Sans `shell=True` et avec une liste, chaque élément est un argument, quoi qu'il contienne : pas de globbing, pas de pipe, pas d'injection. Quand tu as vraiment besoin d'un pipe, chaîne deux `run` en Python, ou fais-le en Python (chapitre 11). Si tu dois découper une ligne de commande écrite par un humain, `shlex.split('ssh -p 2222 user@host "ls -la /tmp"')` donne `['ssh', '-p', '2222', 'user@host', 'ls -la /tmp']`, en respectant les guillemets. Et `shlex.quote(s)` protège une valeur pour un shell distant.

Pour un processus long dont on veut lire la sortie au fil de l'eau (un `tail -f`, un `docker logs -f`), c'est `subprocess.Popen` avec `stdout=subprocess.PIPE` et une boucle `for ligne in proc.stdout:`. Mais `run` couvre 95 % des cas.

### 13.5 Fichiers et système : `pathlib`, `shutil`, `os`

Tu as vu `pathlib` au chapitre 7. Pour l'infra, ce qui sert :

```python
from pathlib import Path
import shutil

conf = Path("/etc/nginx/conf.d")
for fichier in conf.glob("*.conf"):             # itération paresseuse (chapitre 11)
    print(fichier.name, fichier.stat().st_size)
Path("/var/log/app").mkdir(parents=True, exist_ok=True)   # mkdir -p
shutil.copy2(src, dst)                           # cp -p (garde les dates)
shutil.rmtree(dossier)                           # rm -rf, sans filet
shutil.which("docker")                           # le chemin, ou None si absent
shutil.disk_usage("/")                           # (total, used, free) en octets
```

`os.getuid()`, `os.uname()`, `platform.system()`, `socket.gethostname()` pour savoir où on tourne. `tempfile.TemporaryDirectory()` pour un dossier de travail qui disparaît tout seul (un gestionnaire de contexte).

### 13.6 Signaux et arrêt propre

Un `Ctrl-C` envoie `SIGINT`, que Python transforme en exception `KeyboardInterrupt` : un `try / except KeyboardInterrupt` dans `main` suffit pour nettoyer et sortir avec 130 (la convention shell : 128 + numéro du signal). Un `docker stop` ou un `systemctl stop` envoient `SIGTERM`, qui, lui, **tue le processus sans exception** par défaut. Si ton outil doit finir une écriture ou fermer une connexion, il faut installer un gestionnaire :

```python
import signal
import sys

def arret(signum, frame):
    print(f"reçu {signal.Signals(signum).name}, nettoyage", file=sys.stderr)
    # fermer les fichiers, les connexions, écrire l'état...
    sys.exit(130 if signum == signal.SIGINT else 143)

signal.signal(signal.SIGTERM, arret)
signal.signal(signal.SIGINT, arret)
```

C'est le `signal()` du C, avec une fonction Python comme gestionnaire. `sys.exit()` dans le gestionnaire lève `SystemExit`, qui déroule les `finally` et les `with` en cours : les ressources sont libérées. Dans un conteneur, sans ça, Docker attend dix secondes puis envoie `SIGKILL`, et là plus rien ne s'exécute.

### 13.7 Dates et heures : le piège de la naïveté

```python
>>> from datetime import datetime, timezone
>>> from zoneinfo import ZoneInfo
>>> naive = datetime.now()
>>> aware = datetime.now(timezone.utc)
>>> naive.tzinfo, aware.tzinfo
(None, datetime.timezone.utc)
```

Un `datetime` **naïf** n'a pas de fuseau : c'est « 14 h », quelque part. Un `datetime` **conscient** (*aware*) sait de quel fuseau il parle. Comparer ou soustraire un naïf et un conscient lève `TypeError` ; comparer deux naïfs de fuseaux différents donne un résultat faux en silence. La règle pour tout ce qui est infra et logs : **UTC en interne, conversion à l'affichage**.

```python
>>> brux = aware.astimezone(ZoneInfo("Europe/Brussels"))
>>> brux.strftime("%d/%m/%Y %H:%M")
'04/09/2026 14:00'
>>> datetime.fromisoformat("2026-09-04T10:00:00+02:00").astimezone(timezone.utc)
datetime.datetime(2026, 9, 4, 8, 0, tzinfo=datetime.timezone.utc)
>>> datetime.fromtimestamp(1788522583, tz=timezone.utc)
datetime.datetime(2026, 9, 4, 11, 49, 43, tzinfo=datetime.timezone.utc)
```

`fromisoformat` lit ce que produisent les logs, les APIs et `isoformat()` ; `strftime` / `strptime` sont le `strftime` du C avec les mêmes `%d %m %Y %H %M %S`. `zoneinfo` (stdlib depuis 3.9) utilise la base des fuseaux du système. La soustraction de deux `datetime` donne un `timedelta` : `.days`, `.total_seconds()`.

### 13.8 Regex pour parser des sorties

`re` est le module des expressions régulières, avec la syntaxe Perl/PCRE que tu connais de `grep -E` et `sed`. Trois fonctions : `re.search` (trouve n'importe où), `re.match` (au début), `re.findall` (toutes les occurrences). Les groupes nommés rendent le résultat lisible :

```python
>>> import re
>>> m = re.search(r"(\d+)%", " /dev/disk3s1  460Gi  15Gi  81Gi  16% ")
>>> m.group(1)
'16'
>>> for l in ["eth0: 10.0.0.5/24", "lo: 127.0.0.1/8"]:
...     m = re.match(r"(?P<iface>\w+): (?P<ip>[\d.]+)/(?P<masque>\d+)", l)
...     print(m.groupdict())
...
{'iface': 'eth0', 'ip': '10.0.0.5', 'masque': '24'}
{'iface': 'lo', 'ip': '127.0.0.1', 'masque': '8'}
```

Le `r` devant la chaîne (*raw string*) empêche Python d'interpréter les `\` : sans lui, `"\d"` vaudrait… `"\d"` aussi, mais `"\b"` serait un retour arrière. Toujours `r"..."` pour une regex. Un motif utilisé dans une boucle se compile une fois avec `re.compile` (vu au labo 11). Et avant d'écrire une regex pour une sortie de commande, regarde si la commande a une option `--json` ou `--format` : `docker ps --format json`, `kubectl get -o json`, `ip -j addr`. Du JSON se lit avec `json.loads`, sans regex, sans surprise.

### 13.9 Structurer un script d'outillage

Le script de 300 lignes qui fait tout dans l'ordre est celui qu'on n'ose plus toucher. La structure qui tient :

```python
#!/usr/bin/env python3
"""srvctl — gère un inventaire de serveurs. Voir --help."""

import logging
import sys

log = logging.getLogger("srvctl")

# 1. Des fonctions PURES : entrées → sortie, pas de print, pas de sys.exit.
#    Ce sont elles qu'on teste.
def charger_inventaire(chemin) -> list[dict]: ...
def filtrer(serveurs, groupe) -> list[dict]: ...

# 2. Des fonctions qui font des EFFETS (réseau, disque, subprocess), fines,
#    faciles à remplacer par un mock.
def ping(hote, timeout) -> bool: ...

# 3. Un main() qui parse les arguments, colle tout ensemble, gère --dry-run
#    et --verbose, traduit les exceptions en messages et en code de sortie.
def main(argv=None) -> int:
    ...
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(message)s", stream=sys.stderr)
    if args.dry_run:
        log.info("dry-run : %s ne sera pas lancé", commande)
        return 0
    ...

if __name__ == "__main__":
    sys.exit(main())
```

Les habitudes qui vont avec :

- `--dry-run` sur tout ce qui modifie quelque chose : afficher ce qu'on ferait, ne pas le faire. L'option la plus utile d'un outil d'infra.
- `--verbose` qui passe `logging` en `DEBUG` (chapitre 8) : les détails vont sur stderr, le résultat reste sur stdout.
- La première ligne `#!/usr/bin/env python3` plus `chmod +x srvctl.py` : le script se lance comme `./srvctl.py`. Avec un `.venv`, `#!/usr/bin/env -S .venv/bin/python` ou un `Makefile`, ou l'installer.
- `if __name__ == "__main__":` (chapitre 6) : sans ça, `import srvctl` dans un test *lance* le script.

> **Distribuer un outil** : un `pyproject.toml` avec une section `[project.scripts] srvctl = "srvctl:main"` (chapitre 20) fait qu'un `pip install .` crée la commande `srvctl` dans le `PATH` du venv. Pour installer un outil Python de façon globale sans polluer le système, `pipx install .` ou `uv tool install .` lui font un venv privé et exposent seulement la commande. C'est comme ça qu'on installe `ansible`, `black` ou `httpie` sans se battre avec le Python système.

### 13.10 Ce qu'il faut retenir

- argparse pour un script sans dépendance, typer quand l'outil est fait pour durer. `main(argv)` qui prend une liste : testable.
- Contrat shell : code de sortie 0 ou non, résultat sur stdout, le reste sur stderr, `--json` pour les pipes, `isatty()` pour les couleurs.
- `subprocess.run([...], capture_output=True, text=True, check=True, timeout=...)`. Jamais `shell=True` avec une entrée utilisateur.
- `SIGTERM` tue sans exception : installe un gestionnaire si tu as quelque chose à fermer. UTC partout, fuseau seulement à l'affichage.
- Fonctions pures qu'on teste, effets isolés qu'on mocke, un `main()` qui colle. `--dry-run` et `--verbose` sur tout.

**Labo 13** : `srvctl`, un outil typer avec sous-commandes `list`, `ping`, `exec`, `env`, sortie JSON, `--dry-run`, et des tests qui n'appellent jamais le réseau.

---

← [12. Tester avec pytest](12-tests-pytest.md) · [Sommaire](../README.md) · [14. HTTP et APIs, côté client](14-http-et-apis-cote-client.md) →
