# C / Java / Python : la table de correspondance

*Pour qui vient du C (ou de Java, ou du BASIC) et cherche « comment on dit ». La colonne **Piège** signale ce qui se comporte autrement qu'attendu. Renvois vers le [cours](../README.md).*

## Déclarer, typer, nommer

| Quoi | C | Java | Python | Piège |
|---|---|---|---|---|
| Déclarer une variable | `int n = 5;` | `int n = 5;` | `n = 5` | pas de déclaration : la première affectation crée la variable. Une faute de frappe (`nb = 6`) crée une nouvelle variable au lieu d'une erreur. Un linter l'attrape (chap. 20). |
| Type | fixé à la déclaration | fixé | porté par la **valeur**, pas la variable | `n = 5` puis `n = "cinq"` est légal. Mais `5 + "cinq"` est une `TypeError` : dynamique, pas laxiste (chap. 2). |
| Constante | `#define N 5`, `const int` | `static final int N` | `N = 5` (convention majuscules) | rien n'empêche de la modifier. `Final` de `typing` pour que mypy le signale. |
| Entier | 32/64 bits, débordement silencieux | idem | taille illimitée | `2 ** 100` marche. Pas d'overflow, pas d'`unsigned`, pas de `long long`. |
| Flottant | `float`, `double` | idem | `float` = `double` C | `0.1 + 0.2 == 0.3` est `False` partout. `decimal.Decimal` pour l'argent. |
| Booléen | `0` / non-0, `_Bool` | `boolean` | `True` / `False` | `True == 1` et `True + True == 2` : `bool` hérite d'`int`. Sont faux : `0`, `""`, `[]`, `{}`, `None`, `0.0`. |
| Null | `NULL` (0) | `null` | `None` | tester avec `is None`, jamais `== None`. `None` est un objet unique, pas un zéro. |
| Chaîne | `char[]`, `char*`, terminée par `\0` | `String`, immuable | `str`, immuable, Unicode | `s[0] = "x"` est une erreur : on construit une nouvelle chaîne. `len("é") == 1` (caractères, pas octets). Les octets sont `bytes`. |
| Caractère | `'a'` (un `int`) | `char` | `"a"` (une `str` de longueur 1) | pas de type caractère. `ord("a") == 97`, `chr(97) == "a"`. |
| Nommage | libre, souvent `snake_case` | `camelCase`, `PascalCase` | `snake_case` fonctions/variables, `PascalCase` classes, `UPPER` constantes | PEP 8, imposée par ruff. |
| Commentaire | `/* */`, `//` | `/* */`, `//`, `/** */` | `#`, docstring `"""…"""` | pas de commentaire multi-ligne : `#` sur chaque ligne, ou une docstring en première ligne d'une fonction/classe/module. |

## Opérateurs

| Quoi | C / Java | Python | Piège |
|---|---|---|---|
| Division | `7 / 2 == 3` (entiers) | `7 / 2 == 3.5`, `7 // 2 == 3` | `/` donne **toujours** un float. Division entière = `//`. |
| Modulo | `-7 % 2 == -1` | `-7 % 2 == 1` | signe du diviseur, pas du dividende. `-7 // 2 == -4` (arrondi vers le bas). |
| Incrément | `i++`, `++i`, `i += 1` | `i += 1` seulement | `++i` est valide et ne fait rien (`+(+i)`). `i++` est une erreur de syntaxe. |
| Puissance | `pow(a, b)` | `a ** b` | `-2 ** 2 == -4` : `**` prime sur le moins unaire. |
| Égalité | `==` compare valeurs (C) ou références (Java objets) | `==` compare **valeurs** (`__eq__`), `is` compare identités | `a == b` sur deux listes compare le contenu. `is` seulement pour `None`, `True`, `False`. |
| Logique | `&&`, `\|\|`, `!` | `and`, `or`, `not` | `and`/`or` renvoient l'**opérande**, pas un booléen : `"" or "défaut"` vaut `"défaut"`. Pratique, et piège. |
| Bits | `& \| ^ ~ << >>` | identiques | `~x == -x - 1` sur des entiers illimités ; pas de masque implicite sur 32 bits. |
| Ternaire | `c ? a : b` | `a if c else b` | l'ordre est différent : la valeur d'abord. |
| Affectation dans une expression | `if ((n = f()) > 0)` | `if (n := f()) > 0:` | l'opérateur « walrus » `:=`, 3.8+. `=` seul est une instruction, interdit dans un `if`. |
| Comparaisons chaînées | `a < b && b < c` | `a < b < c` | marche, et `a < b > c` aussi (lisible ? non). |

## Structures de contrôle

| Quoi | C / Java | Python | Piège |
|---|---|---|---|
| Blocs | `{ }` | indentation (4 espaces) + `:` | l'indentation **est** la syntaxe. Mélanger tabs et espaces est une erreur. Pas de `;` (toléré, jamais écrit). |
| `if` | `if (c) { } else if { } else { }` | `if c:` / `elif c:` / `else:` | pas de parenthèses obligatoires autour de la condition. |
| `switch` | `switch (x) { case 1: … break; }` | `match x:` / `case 1:` / `case _:` (3.10+) | pas de *fallthrough*, pas de `break`. Et `match` fait bien plus : déstructuration de listes, dicts, objets (chap. 3). Avant 3.10 : chaîne d'`elif` ou un dict de fonctions. |
| `for` compteur | `for (i = 0; i < n; i++)` | `for i in range(n):` | `range(n)` va de 0 à n-1. `range(a, b, pas)`. |
| `for` sur tableau | `for (i = 0; i < n; i++) t[i]` | `for x in t:` ; `for i, x in enumerate(t):` | itérer sur les **éléments**, pas les indices. `for i in range(len(t))` est du C traduit. |
| `while` | `while (c) { }` | `while c:` | pas de `do … while` : `while True:` + `break`. |
| `break` / `continue` | idem | idem | `for … else:` / `while … else:` : le `else` s'exécute si la boucle n'a **pas** été interrompue par `break`. |
| `goto` | existe | non | et on ne le regrette pas. |

## Fonctions

| Quoi | C | Java | Python | Piège |
|---|---|---|---|---|
| Définir | `int f(int a, int b) { return a + b; }` | `static int f(int a, int b)` | `def f(a: int, b: int) -> int: return a + b` | les annotations ne sont **pas** vérifiées à l'exécution (mypy, chap. 20). |
| Prototype / en-tête | `.h` | pas besoin | pas besoin : définir avant d'appeler (à l'exécution) | l'ordre des `def` dans un fichier n'importe pas tant que l'appel a lieu après que le fichier a été lu. |
| Arguments par défaut | non (C), non (Java) | `def f(a, b=2)` | un défaut **mutable** (`b=[]`) est créé une seule fois et partagé entre tous les appels. Écrire `b=None`. |
| Arguments nommés | non | non | `f(b=2, a=1)` | c'est l'usage : `open(p, encoding="utf-8")`. |
| Nombre variable d'arguments | `va_list` | `int... args` | `*args` (tuple), `**kwargs` (dict) | `f(*liste)` et `f(**dict)` dépaquettent à l'appel. |
| Retour multiple | struct ou pointeurs de sortie | objet | `return a, b` (un tuple), `x, y = f()` | c'est un tuple, pas une syntaxe spéciale. |
| Passage | par valeur (copie) ; pointeur pour modifier | par valeur de la référence | par **référence d'objet** | une fonction peut modifier une liste reçue (`l.append`), pas la réaffecter chez l'appelant (`l = []` est local). Chap. 10. |
| Portée | bloc `{ }` | bloc | **fonction** entière ; une variable créée dans un `if` ou un `for` existe après | pas de portée de bloc. `global` / `nonlocal` pour écrire dans une portée englobante ; lire est toujours possible. |
| Fonction anonyme | pointeur de fonction | lambda | `lambda x: x + 1` | une seule expression, pas d'instruction. Au-delà, `def`. |
| Fonctions comme valeurs | pointeur de fonction | interface fonctionnelle | naturel : `f = len; f("abc")` | une fonction est un objet : on la passe, on la stocke, on la décore (chap. 11). |
| `main` | `int main(int argc, char **argv)` | `public static void main(String[] args)` | rien d'obligatoire ; convention `if __name__ == "__main__": main()` | le fichier s'exécute de haut en bas dès l'import. Ce garde évite que l'import lance le programme (chap. 6). |
| Arguments de la ligne de commande | `argv` | `args` | `sys.argv` (liste, `[0]` = script) ; `argparse` (chap. 13) | |

## Données composites

| Quoi | C | Java | Python | Piège |
|---|---|---|---|---|
| Tableau | `int t[10]`, taille fixe, indexé | `int[] t = new int[10]` | `list` : `t = [0] * 10`, taille variable | `[[0] * 3] * 3` crée **trois fois la même ligne** (références, chap. 10). Écrire `[[0] * 3 for _ in range(3)]`. `t[-1]` = dernier élément. `t[10]` sur 10 éléments → `IndexError`, pas de lecture hors limites. |
| Tableau typé compact | `int[]` | `int[]` | `array.array("i")`, `numpy` | une `list` d'entiers est un tableau de **pointeurs** vers des objets `int` : 8 octets + 28 par élément. |
| Structure | `struct { int x; int y; }` | classe avec champs | `@dataclass class P: x: int; y: int` | ou un tuple nommé, ou un dict. Chap. 9. |
| Dictionnaire / table de hachage | à écrire soi-même | `HashMap<K, V>` | `dict` : `{"a": 1}` | clé absente → `KeyError` ; `d.get(k, défaut)` sinon. Les clés doivent être hashables (pas de liste comme clé, un tuple oui). Ordre d'insertion garanti depuis 3.7. |
| Ensemble | à écrire | `HashSet` | `set` : `{1, 2}` | `{}` est un **dict** vide ; un set vide s'écrit `set()`. |
| Énumération | `enum { A, B }` (des `int`) | `enum` (des objets) | `class Couleur(Enum): ROUGE = 1` | des objets, pas des entiers : `Couleur.ROUGE == 1` est `False`. `IntEnum` ou `StrEnum` si on veut la comparaison. |
| Copie | `memcpy`, affectation de struct copie | `.clone()` | `b = a` **ne copie rien** : deux noms pour le même objet | `list(a)`, `a[:]`, `a.copy()`, `dict(d)` : copie superficielle ; `copy.deepcopy(a)` : profonde. Chap. 10. |
| Chaîne de format | `printf("%d %s", n, s)` | `String.format`, `+` | `f"{n} {s}"`, `print(n, s)` | `print` ajoute un `\n` (`end=""` pour l'éviter) et sépare par un espace (`sep=`). `%` et `.format()` existent encore, à lire, pas à écrire. |

## Mémoire, pointeurs, objets

| Quoi | C | Java | Python | Piège |
|---|---|---|---|---|
| Allocation | `malloc` / `free` | `new`, GC | automatique : tout est objet alloué sur le tas | pas de `free` : comptage de références + ramasse-miettes pour les cycles (chap. 10). |
| Pointeur | `int *p = &n; *p = 3;` | références implicites | toute variable **est** une référence (une étiquette sur un objet) | pas d'arithmétique de pointeurs, pas d'adresse manipulable. `id(x)` donne un identifiant unique (l'adresse en CPython), en lecture seule. |
| Mutabilité | tout est modifiable | dépend de la classe | **immuables** : `int`, `float`, `str`, `tuple`, `frozenset`, `bytes` ; **mutables** : `list`, `dict`, `set`, objets | `s += "x"` crée une nouvelle chaîne ; `l += [x]` modifie la liste en place. Même syntaxe, deux comportements. |
| Identité vs égalité | `p == q` compare des adresses | `==` références, `.equals()` valeurs | `is` identité, `==` valeur | dans le REPL, `a = 100` puis `b = 100` donnent `a is b` → `True` (cache des petits entiers), mais avec `1000` → `False`. Ne jamais utiliser `is` pour des valeurs. |
| Struct vs classe | `struct` sans méthodes | classe | `class`, ou `@dataclass` qui écrit `__init__`, `__repr__`, `__eq__` pour toi | pas de `private` : `_x` est une convention, `__x` est renommé (name mangling), rien n'est inaccessible. |
| `this` | pointeur explicite dans le code C « objet » | implicite | `self`, **explicite**, premier paramètre de chaque méthode | oublier `self` dans la signature est l'erreur n°1 des débutants : `TypeError: f() takes 0 positional arguments but 1 was given`. |
| Héritage | non | `extends`, simple | `class B(A):`, multiple possible | `super().__init__()` n'est pas appelé automatiquement. Préférer la composition et les `Protocol` (chap. 9). |
| Interface | non | `interface`, `implements` | duck typing : « si ça a `.read()`, c'est un fichier » ; `Protocol` pour le vérifier statiquement, `abc.ABC` pour l'imposer | on ne déclare pas qu'on implémente : on implémente. |
| Destructeur | `free` à la main | `finalize` (déconseillé) | `__del__` (déconseillé) ; `with` + `__enter__`/`__exit__` pour libérer une ressource | fermer un fichier ou une connexion : `with`, jamais `__del__`. Chap. 11. |
| Taille en mémoire | `sizeof` | – | `sys.getsizeof(x)` | un `int` fait 28 octets, une liste vide 56. Python ne joue pas dans la même catégorie que C. |
| Alignement, endianness, bits | quotidien | rare | `struct.pack("<I", n)`, `int.to_bytes(4, "little")`, `int.from_bytes` | ça existe, pour parler à du C, du réseau ou du binaire. |

## Erreurs

| Quoi | C | Java | Python | Piège |
|---|---|---|---|---|
| Signaler | code de retour, `errno` | `throw new X()` | `raise X("msg")` | une fonction qui échoue **lève**, elle ne renvoie pas `-1`. Renvoyer `None` pour « pas trouvé » est acceptable ; renvoyer `None` pour « erreur » ne l'est pas. |
| Attraper | `if (r < 0)` | `try { } catch (X e) { } finally { }` | `try:` / `except X as e:` / `else:` / `finally:` | `except:` nu attrape aussi `KeyboardInterrupt` : toujours nommer le type. `except Exception` au pire. |
| Exceptions vérifiées | – | `throws` obligatoire | aucune déclaration | on ne sait pas ce qu'une fonction peut lever sans lire sa doc. |
| Chaîner | – | `cause` | `raise Y("…") from e` | la trace montre les deux. `from None` pour masquer l'originale. |
| Segfault, comportement indéfini | quotidien | `NullPointerException` | n'existe pas (hors extension C buggée) | tout est une exception avec un traceback lisible (chap. 1). |
| Assertion | `assert()` (`NDEBUG`) | `assert` (désactivé par défaut) | `assert c, "msg"` (désactivé avec `-O`) | pour les invariants de développement, jamais pour valider une entrée utilisateur. |

## Compilation, exécution, organisation

| Quoi | C | Java | Python | Piège |
|---|---|---|---|---|
| Chaîne d'outils | préprocesseur → compilateur → éditeur de liens → exécutable natif | `javac` → bytecode `.class` → JVM (JIT) | source → bytecode `.pyc` (automatique, caché dans `__pycache__`) → interpréteur CPython | pas d'étape de build à lancer. Les erreurs de type n'apparaissent qu'à l'exécution de la ligne fautive (d'où mypy et les tests). |
| Vitesse | référence | 1 à 3× plus lent | 10 à 100× plus lent en boucle pure | mais les bibliothèques (numpy, sqlite, ssl, json…) sont en C. Le Python n'est souvent que la colle. Chap. 10. |
| Fichier d'en-tête / import | `#include "x.h"` + lier `x.o` | `import paquet.Classe` | `import module` ; `from module import nom` | un module est **exécuté** à son premier import (une fois, puis mis en cache dans `sys.modules`). Pas de `#ifndef` : le cache s'en charge. |
| Préprocesseur | `#define`, `#ifdef` | – | aucun | conditions à l'exécution : `if sys.platform == "win32":`, `if sys.version_info >= (3, 12):`. |
| Unité de code | fichier `.c` | classe = fichier | module = fichier `.py` ; paquet = dossier avec `__init__.py` | plusieurs classes et fonctions par fichier, c'est normal. Chap. 6. |
| Espace de noms | global, préfixes `mod_` | packages | chaque module est un espace de noms : `os.path.join`, `json.loads` | `from x import *` pollue : à éviter hors REPL. |
| Bibliothèques | à installer par l'OS, `-lfoo` | Maven / Gradle, `pom.xml` | `pip` / `uv`, `pyproject.toml`, un `.venv` par projet | jamais `pip install` hors d'un venv (chap. 1). |
| Build / dépendances | `make`, `Makefile` | `mvn`, `gradle` | `pyproject.toml`, `uv sync`, `python -m build` (chap. 20) | pas de `Makefile` nécessaire, mais on en écrit souvent un petit pour les raccourcis. |
| Exécutable | `./a.out` | `java -jar x.jar` | `python3 script.py` ; commande installée via `[project.scripts]` ; image Docker | pas d'exécutable autonome par défaut (PyInstaller, Nuitka existent, avec des compromis). |
| Débogueur | `gdb`, `lldb` | IDE | `breakpoint()` dans le code → `pdb` ; IDE ; `python3 -i` | `print()` reste honnête ; `rich.print` et `pprint` pour les structures. |
| Threads | `pthread`, vrais parallélisme | vrais threads | `threading` : threads réels mais **un seul exécute du Python à la fois** (GIL) ; `multiprocessing` pour le CPU ; `asyncio` pour l'I/O | pour du calcul, les threads ne servent à rien ; pour de l'I/O (réseau, disque), ils servent, et `asyncio` sert mieux. Chap. 10 et 15. 3.13 a un mode sans GIL, expérimental. |
| Entrées / sorties | `printf`, `scanf`, `fopen` | `System.out`, `Scanner` | `print()`, `input()`, `open()` avec `with` | `input()` renvoie toujours une `str` : `int(input())`. `open()` sans `encoding=` dépend de la plateforme : toujours le préciser. |

## Le réflexe à prendre

En C, tu penses en octets et en adresses ; en Java, en classes et en interfaces. En Python, pense en **objets et en étiquettes** : chaque valeur est un objet quelque part, chaque variable est un nom collé dessus, et une affectation ne fait que déplacer l'étiquette. Le reste (mutabilité, passage d'arguments, copies, `is` contre `==`) en découle. C'est le chapitre 10, et c'est celui qu'il faut relire si quelque chose « ne fait pas ce que je veux ».
