# cours-python — Python de zéro à FastAPI, pour qui a déjà codé

```
$ whoami
stranix · le renard qui aime savoir ce qui se passe sous le capot

$ cat cours-python/README.md
```

Un cours en français, par **Gilles Fauvie** ([stranix.net](https://stranix.net)).

Tu as déjà codé. Du C, du BASIC sur un Commodore 64, un peu de Java, un peu de Python copié-collé qui marche sans que tu saches trop pourquoi. Tu n'as pas besoin qu'on t'explique ce qu'est une boucle. Tu as besoin qu'on t'explique **ce que Python fait différemment**, pourquoi, et comment on s'en sert aujourd'hui pour écrire des scripts, des outils en ligne de commande et des API web.

Ce dépôt est un cours **qui part de zéro** mais qui ne traîne pas : chaque notion est comparée à ce que tu connais déjà (C, Java, BASIC), et on va jusqu'à des sujets qu'on ne trouve pas dans les tutos pour débutants : ce qui se passe sous le capot (références, GIL, bytecode), l'asynchrone, les web services (REST, SOAP, GraphQL, gRPC, WebSocket… et pourquoi ils existent), FastAPI, les bases de données, les tests, l'empaquetage et le déploiement en Docker.

Tout a été écrit et exécuté avec **Python 3.13** sur un Mac, mais rien n'est spécifique à macOS : Linux et Windows (WSL ou natif) font aussi bien.

## Comment ça marche

Vingt-deux chapitres, chacun suivi d'un labo. Le labo donne un squelette à compléter avec des `# TODO`, une solution commentée ligne par ligne dans `solution/`, et, à partir du chapitre 12, des tests `pytest` qui te disent si c'est bon. Compte une à deux heures par chapitre.

| Chapitre | Labo |
|---|---|
| [0. Pourquoi Python, et pourquoi maintenant](cours/00-pourquoi-python.md) | — |
| [1. Installer, outiller, lancer](cours/01-installer-et-outiller.md) | [01-hello](labs/01-hello/README.md) |
| [2. Variables, types, chaînes](cours/02-variables-types-chaines.md) | [02-convertisseur](labs/02-convertisseur/README.md) |
| [3. Contrôle : conditions et boucles](cours/03-controle-conditions-boucles.md) | [03-devine-nombre](labs/03-devine-nombre/README.md) |
| [4. Collections : listes, tuples, dicts, sets](cours/04-collections.md) | [04-inventaire](labs/04-inventaire/README.md) |
| [5. Fonctions](cours/05-fonctions.md) | [05-boite-a-outils](labs/05-boite-a-outils/README.md) |
| [6. Modules, paquets, pip et venv](cours/06-modules-paquets-pip.md) | [06-mon-paquet](labs/06-mon-paquet/README.md) |
| [7. Fichiers, chemins, JSON, CSV](cours/07-fichiers-json-csv.md) | [07-carnet-adresses](labs/07-carnet-adresses/README.md) |
| [8. Erreurs, exceptions, logging](cours/08-erreurs-exceptions-logging.md) | [08-robuste](labs/08-robuste/README.md) |
| [9. Classes et objets](cours/09-classes-et-objets.md) | [09-compte-bancaire](labs/09-compte-bancaire/README.md) |
| [10. Sous le capot : références, mémoire, GIL, bytecode](cours/10-sous-le-capot.md) | [10-references](labs/10-references/README.md) |
| [11. Itérateurs, générateurs, décorateurs, `with`](cours/11-iterateurs-generateurs-decorateurs.md) | [11-pipeline-logs](labs/11-pipeline-logs/README.md) |
| [12. Tester avec pytest](cours/12-tests-pytest.md) | [12-tests](labs/12-tests/README.md) |
| [13. Ligne de commande et scripts DevOps](cours/13-ligne-de-commande-et-devops.md) | [13-cli-devops](labs/13-cli-devops/README.md) |
| [14. HTTP et APIs, côté client](cours/14-http-et-apis-cote-client.md) | [14-client-api](labs/14-client-api/README.md) |
| [15. Asynchrone : asyncio, async/await](cours/15-async.md) | [15-async](labs/15-async/README.md) |
| [16. Web services : REST, SOAP, GraphQL, gRPC, WebSocket](cours/16-web-services-panorama.md) | [16-trois-facons](labs/16-trois-facons/README.md) |
| [17. FastAPI : premiers pas](cours/17-fastapi-premiers-pas.md) | [17-fastapi-todo](labs/17-fastapi-todo/README.md) |
| [18. Bases de données : sqlite3, SQLAlchemy, SQLModel](cours/18-bases-de-donnees.md) | [18-sqlite-sqlmodel](labs/18-sqlite-sqlmodel/README.md) |
| [19. FastAPI avancé : dépendances, auth, tests, Docker](cours/19-fastapi-avance.md) | [19-api-complete](labs/19-api-complete/README.md) |
| [20. Qualité, empaquetage, déploiement](cours/20-qualite-empaqueter-deployer.md) | [20-deploiement](labs/20-deploiement/README.md) |
| [21. Projet final et pour aller plus loin](cours/21-projet-final-et-suite.md) | [21-projet](labs/21-projet/README.md) |

Antisèches : [tools/python-antiseche.md](tools/python-antiseche.md) (la syntaxe sur deux pages) et [tools/c-vs-python.md](tools/c-vs-python.md) (la table de correspondance C / Java / Python).

## Démarrer en deux minutes

```bash
git clone https://github.com/stranix79/cours-python.git
cd cours-python
python3 --version               # 3.11 minimum, 3.13 recommandé
python3 -m venv .venv           # un environnement isolé pour le cours
source .venv/bin/activate       # Windows : .venv\Scripts\activate
pip install -r requirements.txt # tout ce qu'il faut pour les 22 labos
cd labs/01-hello
python3 hello.py                # ton premier script
python3 solution/hello.py       # la version corrigée, commentée
```

À partir du labo 12 : `pytest` dans le dossier du labo te dit si ta version passe, et `SOLUTION=1 pytest` lance les mêmes tests sur la solution.

## Ce que tu sauras faire à la fin

- écrire du Python idiomatique, pas du C traduit mot à mot ;
- structurer un projet en modules et paquets, avec un `pyproject.toml`, des tests et un linter ;
- lire et écrire des fichiers, du JSON, du CSV, parler à une base SQLite ;
- écrire des outils en ligne de commande propres pour ton quotidien DevOps ;
- appeler des APIs HTTP, en synchrone et en asynchrone ;
- expliquer la différence entre REST, SOAP, GraphQL, gRPC et WebSocket, et choisir ;
- construire, tester, documenter et déployer une API FastAPI avec authentification et base de données ;
- comprendre ce qui se passe sous le capot : références, mutabilité, GIL, bytecode.

## Pourquoi en français, pourquoi comme ça

Parce que les cours Python en français s'arrêtent trop souvent à la boucle `for`, et que ceux qui vont jusqu'à FastAPI supposent que tu as déjà tout le reste. Ici, on part de zéro, on compare à ce que tu connais (C, Java, BASIC), et on va jusqu'au bout : une API en production dans un conteneur.

Licence MIT. Le cours est vivant : une erreur, une question, une idée de labo, ouvre une issue. On en parle aussi sur [stranix.net](https://stranix.net).

## Du même auteur

Les autres cours, même esprit :

- [cours-go](https://github.com/stranix79/cours-go) : Go de zéro à la prod, même format, même public.
- [asm-m1](https://github.com/stranix79/asm-m1) : l'assembleur ARM64 sur Mac Apple Silicon, pour voir ce qu'il y a sous le capot.

Et le reste :

- [stranix.net](https://stranix.net) : le blog, où l'on parle de ce genre de choses.
- [Deckhand](https://deckhand.show) : des présentations HTML écrites en Markdown.
- [Chutag](https://chutag.stranix.net) : des tags QR pour retrouver ses objets perdus (bêta).
- [apps.stranix.net](https://apps.stranix.net) : les apps macOS de Stranix.
- [CODE79](https://code79.com) : l'atelier devops derrière tout ça.

```
$ ls /ventures
code79.com     consulting/
sygnet.app     saas/
stranix.net    blog/          ← tu es ici
```
