# Antisèche Python 3.13

*La syntaxe sur deux pages. Les renvois « chap. N » pointent vers le [cours](../README.md).*

## Types de base (chap. 2)

| Type | Exemple | Notes |
|---|---|---|
| `int` | `42`, `0xFF`, `1_000_000`, `2 ** 100` | taille illimitée |
| `float` | `3.14`, `1e-9`, `float("inf")` | double 64 bits, `0.1 + 0.2 != 0.3` |
| `bool` | `True`, `False` | sous-type d'`int` : `True + 1 == 2` |
| `str` | `"a"`, `'a'`, `"""multi\nligne"""` | immuable, Unicode |
| `bytes` | `b"\x00\xff"`, `"é".encode()` | octets bruts |
| `None` | `None` | l'absence de valeur ; tester avec `is None` |

```python
int("42"); float("3.5"); str(42); bool(0)   # conversions ; bool("") est False
7 // 2, 7 % 2, 7 / 2, divmod(7, 2)          # 3, 1, 3.5, (3, 1)
round(2.675, 2); abs(-3); min(1, 2); max([1, 2]); sum([1, 2]); pow(2, 10)
isinstance(x, int); type(x) is int; isinstance(x, (int, float))
```

## Chaînes (chap. 2)

```python
s = "Bonjour"
s[0], s[-1], s[1:4], s[::-1]          # 'B', 'r', 'onj', inversée
len(s); "on" in s; s.upper(); s.lower(); s.title(); s.strip(); s.replace("j", "J")
s.split(","); ",".join(["a", "b"]); s.startswith("Bon"); s.find("j"); s.count("o")
f"{nom} a {age} ans"                  # f-string (chap. 2)
f"{x:.2f} {n:>5} {n:05d} {p:.1%} {big:,} {v!r} {x=}"   # format : décimales, largeur, zéros, %, milliers, repr, debug
"%s %d" % (a, b); "{} {}".format(a, b)  # les anciennes façons, à reconnaître
r"C:\chemin\brut"                     # raw : pas d'échappement
"é".encode("utf-8"); b"\xc3\xa9".decode()
```

## Collections (chap. 4)

| Type | Littéral | Mutable | Ordonné | Usage |
|---|---|---|---|---|
| `list` | `[1, 2, 3]` | oui | oui | séquence qui change |
| `tuple` | `(1, 2)`, `1,` | non | oui | enregistrement, clé de dict |
| `dict` | `{"a": 1}` | oui | insertion | clé → valeur |
| `set` | `{1, 2}`, `set()` | oui | non | unicité, appartenance O(1) |
| `frozenset` | `frozenset({1})` | non | non | set hashable |

```python
l = [3, 1, 2]
l.append(4); l.extend([5]); l.insert(0, 9); l.pop(); l.pop(0); l.remove(3); l.index(2)
l.sort(); l.sort(key=len, reverse=True); sorted(l); l.reverse(); reversed(l)
l[1:3]; l[::2]; l[-2:]; del l[0]; l.copy(); l[:]     # tranches ; copie superficielle
d = {"a": 1}
d["b"] = 2; d.get("z", 0); d.setdefault("c", []); d.pop("a"); d.update({"x": 1})
d.keys(); d.values(); d.items(); "a" in d; {**d, "y": 2}; d | {"y": 2}
s = {1, 2}; s.add(3); s | {4}; s & {1}; s - {1}; s ^ {1, 9}; s.issubset({1, 2, 3})
a, b = 1, 2; a, b = b, a; premier, *reste = [1, 2, 3]; x, (y, z) = 1, (2, 3)
```

Compréhensions (chap. 4) : `[x * 2 for x in l if x > 1]`, `{k: v for k, v in paires}`, `{x % 3 for x in l}`, `(x for x in l)` (générateur, paresseux).

Fonctions sur itérables : `len`, `sum`, `min`, `max`, `sorted`, `reversed`, `any`, `all`, `enumerate(l, start=1)`, `zip(a, b, strict=True)`, `map(f, l)`, `filter(f, l)`, `range(0, 10, 2)`.

`collections` : `Counter(mots).most_common(3)`, `defaultdict(list)`, `deque(maxlen=10)`, `namedtuple`, `OrderedDict`, `ChainMap`.

## Contrôle (chap. 3)

```python
if x > 0 and not y or z: ...
elif x == 0: ...
else: ...
valeur = a if cond else b                  # ternaire
for i, x in enumerate(l): ...              # for … else : le else s'exécute sans break
while cond: ...  # break, continue
match commande.split():                    # 3.10+ (chap. 3)
    case ["go", direction]: ...
    case ["quit" | "exit"]: ...
    case [x, *reste] if len(reste) > 2: ...
    case {"action": a, **rest}: ...
    case Point(x=0, y=0): ...
    case _: ...
```

Opérateurs : `and or not`, `== != < <= > >=`, `is`, `is not`, `in`, `not in`, `+ - * / // % **`, `& | ^ ~ << >>`, `:=` (walrus : `if (n := len(l)) > 3:`). Pas de `++`, pas de `switch`, pas de `? :`.

## Fonctions (chap. 5)

```python
def f(a, b=2, *args, c, d=4, **kwargs) -> int:
    """Docstring : première ligne = résumé."""
    return a + b
def g(pos_seul, /, normal, *, mot_cle_seul): ...   # / et * forcent le mode de passage
f(1, c=3); f(*[1, 2], **{"c": 3})              # dépaquetage à l'appel
lambda x, y=1: x + y                            # fonction anonyme, une expression
def compteur():
    n = 0
    def inc():
        nonlocal n                              # global pour une variable de module
        n += 1
        return n
    return inc
```

**Piège** : défaut mutable `def f(l=[])` → partagé entre appels ; écrire `l=None` puis `l = l or []`.

Annotations (chap. 5, 20) : `def f(x: int, y: str | None = None) -> list[int]:`, `dict[str, list[int]]`, `Callable[[int], str]`, `Iterable[T]`, `TypedDict`, `Protocol`, `Literal["a", "b"]`, `Final`, `type Alias = int | str` (3.12), `def premier[T](xs: list[T]) -> T` (3.12).

## Classes (chap. 9)

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, order=True, slots=True)
class Point:
    x: float
    y: float = 0.0
    tags: list[str] = field(default_factory=list)

class Compte:
    taux = 0.02                                 # attribut de classe (partagé)
    def __init__(self, solde: float) -> None:
        self._solde = solde                     # _ : privé par convention ; __x : name mangling
    def __repr__(self) -> str: return f"Compte({self._solde})"
    def __str__(self) -> str: ...
    def __eq__(self, other): ...                # + __hash__, __lt__, __len__, __getitem__,
    def __enter__(self): ...                    #   __iter__, __contains__, __call__, __add__
    def __exit__(self, *exc): ...
    @property
    def solde(self) -> float: return self._solde
    @solde.setter
    def solde(self, v: float) -> None: ...
    @classmethod
    def depuis_json(cls, s: str) -> "Compte": ...
    @staticmethod
    def valide(s: float) -> bool: ...

class Epargne(Compte):
    def __init__(self, solde, taux):
        super().__init__(solde)
```

`isinstance`, `issubclass`, `hasattr`, `getattr(obj, "x", défaut)`, `setattr`, `vars(obj)`, `obj.__dict__`, `type(obj).__name__`, `abc.ABC` + `@abstractmethod`, `enum.Enum` / `StrEnum` / `IntEnum` / `Flag`, `typing.Protocol`, `functools.total_ordering`, `functools.cached_property`.

## Exceptions (chap. 8)

```python
try:
    r = int(s)
except ValueError as e:
    print(e)                                    # e.args, type(e).__name__
except (TypeError, KeyError):
    raise                                       # relance telle quelle
except Exception as e:
    raise RuntimeError("contexte") from e       # chaîne ; `from None` pour masquer
else:
    ...                                         # si aucune exception
finally:
    ...                                         # toujours
class ErreurConfig(Exception): pass
raise ErreurConfig(f"clé manquante : {cle}")
try: ...
except* ValueError as eg: ...                   # 3.11 : ExceptionGroup
```

Hiérarchie utile : `Exception` > `ValueError`, `TypeError`, `KeyError`, `IndexError`, `AttributeError`, `OSError` (> `FileNotFoundError`, `PermissionError`, `ConnectionError`, `TimeoutError`), `RuntimeError`, `NotImplementedError`, `StopIteration`. Hors `Exception` : `KeyboardInterrupt`, `SystemExit`. `assert cond, "msg"` (désactivé avec `-O`). `logging` : `logging.basicConfig(level=logging.INFO)`, `log = logging.getLogger(__name__)`, `log.info("x=%s", x)`, `log.exception("…")` dans un `except`.

## Fichiers et chemins (chap. 7)

```python
from pathlib import Path
p = Path.home() / "projet" / "config.json"
p.exists(); p.is_file(); p.name; p.stem; p.suffix; p.parent; p.resolve(); p.mkdir(parents=True, exist_ok=True)
p.read_text(encoding="utf-8"); p.write_text(s); p.read_bytes(); p.unlink(); p.rename(q)
list(Path(".").glob("*.py")); Path(".").rglob("*.log"); p.stat().st_size; p.iterdir()
with open(p, encoding="utf-8") as f:          # modes : r w a x, + b ; encoding TOUJOURS
    for ligne in f: ...                         # f.read(), f.readlines(), f.write()
import json; json.load(f); json.loads(s); json.dump(obj, f, indent=2, ensure_ascii=False); json.dumps(obj)
import csv; csv.DictReader(f); csv.DictWriter(f, fieldnames=[...]); csv.reader(f, delimiter=";")
import shutil, tempfile, os; shutil.copy2(a, b); shutil.rmtree(d); tempfile.TemporaryDirectory(); os.environ.get("HOME")
```

## Modules et paquets (chap. 6)

```python
import os, sys                                  # un par ligne en vrai (ruff E401)
import numpy as np
from pathlib import Path
from . import voisin; from .sous import x       # imports relatifs, dans un paquet
if __name__ == "__main__": main()               # exécuté seulement si lancé directement
sys.path; sys.argv; sys.exit(1); sys.stdin; sys.stderr
__file__; __name__; __doc__; importlib.reload(m); importlib.metadata.version("pkg")
```

Un dossier avec `__init__.py` = paquet. `python3 -m paquet.module` lance un module avec les imports qui marchent. `__all__ = [...]` contrôle `from m import *`.

## Itérateurs, générateurs, décorateurs, `with` (chap. 11)

```python
def compte(n):                                  # générateur : lazy, un yield à la fois
    for i in range(n): yield i
it = iter(l); next(it, défaut)                  # protocole : __iter__ / __next__
gen = (x * x for x in range(10)); sum(gen)      # expression génératrice
yield from autre_generateur()
import itertools as it; it.chain(a, b); it.islice(g, 5); it.count(1); it.cycle(l); it.product(a, b); it.groupby(l, key=f); it.batched(l, 3)  # 3.12
import functools; @functools.wraps(f); functools.partial(f, 1); functools.reduce(op, l); @functools.lru_cache(maxsize=128); @functools.cache

def chrono(f):                                  # décorateur
    @functools.wraps(f)
    def wrapper(*a, **k):
        t = time.perf_counter(); r = f(*a, **k); print(time.perf_counter() - t); return r
    return wrapper
@chrono
def lent(): ...

from contextlib import contextmanager, suppress, closing, ExitStack
@contextmanager
def ouvert(p):
    f = open(p)
    try: yield f
    finally: f.close()
with ouvert("x") as f, suppress(FileNotFoundError): ...
```

## Async (chap. 15)

```python
import asyncio
async def tache(n):
    await asyncio.sleep(1)                      # await : cède la main ; jamais time.sleep ici
    return n
async def main():
    r = await asyncio.gather(tache(1), tache(2), return_exceptions=True)
    t = asyncio.create_task(tache(3)); t.cancel()
    async with asyncio.timeout(5): ...          # 3.11
    async with asyncio.TaskGroup() as tg: tg.create_task(tache(4))   # 3.11
    await asyncio.wait_for(coro, 2); await asyncio.to_thread(bloquant)
    q: asyncio.Queue[int] = asyncio.Queue(); await q.put(1); await q.get()
    async for x in agen(): ...                  # async def + yield = générateur async
asyncio.run(main())
```

`httpx.AsyncClient()` pour HTTP, `asyncio.open_connection` pour TCP, `asyncio.create_subprocess_exec` pour les processus. Sync et bloquant → `asyncio.to_thread`. Concurrence CPU → `multiprocessing` / `concurrent.futures.ProcessPoolExecutor` (chap. 10, GIL).

## Bibliothèque standard à connaître

| Module | Pour |
|---|---|
| `sys`, `os`, `platform` | interpréteur, environnement, système |
| `pathlib`, `shutil`, `tempfile`, `glob` | fichiers |
| `json`, `csv`, `tomllib` (3.11), `configparser`, `xml.etree`, `sqlite3` | formats et BDD (chap. 7, 18) |
| `argparse`, `subprocess`, `shlex`, `signal` | ligne de commande, processus (chap. 13) |
| `datetime`, `zoneinfo`, `time`, `calendar` | dates : `datetime.now(UTC)`, `.isoformat()`, `strftime("%Y-%m-%d")`, `timedelta(days=1)` |
| `re` | regex : `re.search`, `re.findall`, `re.sub`, `re.compile`, groupes nommés `(?P<x>…)` |
| `logging`, `traceback`, `warnings` | diagnostics (chap. 8) |
| `collections`, `itertools`, `functools`, `operator` | outils sur les données |
| `dataclasses`, `enum`, `typing`, `abc` | modélisation (chap. 9) |
| `math`, `statistics`, `random`, `secrets`, `decimal`, `fractions` | nombres ; `secrets` pour ce qui est sensible |
| `hashlib`, `hmac`, `base64`, `uuid` | empreintes, encodages, identifiants |
| `socket`, `ssl`, `ipaddress`, `urllib`, `http.server`, `http.client`, `email`, `smtplib` | réseau (chap. 14, 16) |
| `threading`, `multiprocessing`, `concurrent.futures`, `asyncio`, `queue` | concurrence (chap. 10, 15) |
| `unittest`, `doctest`, `unittest.mock` | tests (pytest est mieux, chap. 12) |
| `pprint`, `textwrap`, `string`, `difflib`, `struct`, `array`, `copy`, `pickle`, `gzip`, `zipfile`, `tarfile` | divers |
| `dis`, `inspect`, `gc`, `weakref`, `timeit`, `cProfile` | sous le capot (chap. 10) |

## Commandes

```bash
python3 -m venv .venv && source .venv/bin/activate    # chap. 1 ; deactivate pour sortir
python3 -i script.py            # REPL après exécution     python3 -c "code"
python3 -m module               # module comme programme   python3 -X importtime script.py
python3 -m pdb script.py        # débogueur ; breakpoint() dans le code
pip install -r requirements.txt ; pip install -e ".[dev]" ; pip freeze ; pip list --outdated ; pip show pkg
uv init ; uv add httpx ; uv add --dev pytest ; uv sync ; uv run pytest ; uv lock ; uv build ; uvx ruff check .   # chap. 20
pipx install ruff               # un outil CLI dans son propre venv
pytest -q ; pytest -x -k "nom" ; pytest -v --tb=short ; pytest --lf ; pytest -s   # chap. 12
ruff check . --fix ; ruff format . ; mypy src ; mypy --strict src        # chap. 20
python3 -m build ; twine upload dist/*
uvicorn app.main:app --reload   # chap. 17
python3 -m http.server 8000 ; python3 -m json.tool f.json ; python3 -m timeit "sum(range(1000))"
```
