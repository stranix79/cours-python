# 21. Projet final et pour aller plus loin

*Python de zéro à FastAPI — chapitre 21 sur 21.* ← [20. Qualité, empaquetage, déploiement](20-qualite-empaqueter-deployer.md) · [Sommaire](../README.md)

> 🧪 Labo associé : [`labs/21-projet`](../labs/21-projet/README.md)

Vingt chapitres, vingt labos, chacun sur un sujet. Il manque une chose : un projet où tout se tient ensemble, où le choix d'un type dans `models.py` a des conséquences dans `api.py`, où le worker async doit cohabiter avec une base synchrone, où les tests doivent lancer un vrai serveur. C'est ce chapitre. Il n'apprend pas de nouvelle syntaxe : il te donne un cahier des charges, une architecture, un ordre de marche, et te laisse faire.

### 21.1 Le projet : statusboard

Un service de surveillance, comme un Uptime Kuma de poche. Tu lui donnes des cibles (un site en HTTP, un port TCP, une machine à pinger), il les vérifie à intervalle régulier, garde l'historique, expose l'état par une API, pousse les changements en temps réel, et se pilote en ligne de commande. C'est un vrai outil d'infra, de la taille d'un week-end, qui utilise tout ce que le cours a vu.

Le cahier des charges complet est dans le [README du labo](../labs/21-projet/README.md). En résumé :

| Brique | Ce qu'elle fait | Chapitres mobilisés |
|---|---|---|
| Modèles et base | `Target`, `Check`, `User` en SQLModel, SQLite | 9, 18 |
| Vérifications | HTTP (httpx), TCP (`asyncio.open_connection`), ping (sous-processus) | 14, 15 |
| Worker | tâche asyncio, vérifie en parallèle les cibles dues, publie un événement | 11, 15 |
| API | FastAPI, JWT, CRUD des cibles, état courant, SSE | 16, 17, 19 |
| CLI | typer : `add`, `list`, `status`, `check`, `serve` | 13 |
| Configuration | variables d'environnement `STATUSBOARD_*` | 20 |
| Tests | serveur HTTP local dans un thread, TestClient, `CliRunner` | 12, 19 |
| Livraison | `pyproject.toml`, ruff, Dockerfile, compose | 20 |

### 21.2 Architecture

```
                    ┌────────────────────────────────────────────────────┐
  statusboard CLI   │  processus uvicorn                                 │
  (add/list/status) │                                                    │
        │           │   ┌────────────┐   publish   ┌──────────────┐      │
        │           │   │  worker    │ ──────────▶ │  Broadcaster │      │
        │           │   │  (asyncio) │             │  (bus.py)    │      │
        │           │   └─────┬──────┘             └──────┬───────┘      │
        │           │         │ run_check                 │ Queue par    │
        │           │         ▼                           │ abonné       │
        │           │   ┌────────────┐                    ▼              │
        │           │   │  checks.py │             ┌──────────────┐      │
        │           │   │ http/tcp/  │             │  GET /events │──────┼──▶ curl -N,
        │           │   │ ping       │             │  (SSE)       │      │    navigateur
        │           │   └────────────┘             └──────────────┘      │
        │           │         │ Check                                    │
        ▼           │         ▼                                          │
   ┌──────────┐     │   ┌────────────┐      ┌──────────────────────┐     │
   │  SQLite  │◀────┼──▶│  db.py     │◀────▶│  api.py (FastAPI)    │◀────┼──▶ clients HTTP,
   │ (fichier)│     │   │  SQLModel  │      │  /token /targets     │     │    /docs
   └──────────┘     │   └────────────┘      │  /status /health     │     │
                    │                       └──────────────────────┘     │
                    └────────────────────────────────────────────────────┘
```

Trois décisions à comprendre avant de coder, parce qu'elles reviennent dans tout projet de ce genre :

**Le worker vit dans le processus de l'API.** Il est lancé par le `lifespan` avec `asyncio.create_task()` et annulé à l'arrêt. Un seul processus, un seul déploiement, une seule base. C'est le bon choix jusqu'à quelques centaines de cibles. Au-delà, le worker devient un processus séparé et le bus d'événements passe par Redis ; l'architecture ne change pas, seul le transport change.

**La base est synchrone, le worker est asynchrone.** SQLModel avec SQLite est synchrone : chaque requête bloque la boucle d'événements le temps de son exécution. Sur SQLite en local, c'est une milliseconde, ça ne se voit pas. Ce qui compte, c'est de **ne pas garder de session ouverte pendant un `await` long** : on lit ce qu'il faut, on ferme, on fait la vérification réseau, on rouvre pour écrire. Le jour où ça ne suffit plus, SQLAlchemy a un mode async (`create_async_engine`, `AsyncSession`) et le reste du code ne bouge pas.

**Le bus d'événements est une `asyncio.Queue` par abonné.** Quand un client se connecte à `/events`, il reçoit sa propre file ; le worker met chaque résultat dans toutes les files. Un client lent ne ralentit pas les autres, un client qui part est retiré par le `finally` du context manager. C'est le patron *publish/subscribe* dans sa forme la plus simple, et c'est exactement ce que Redis pub/sub ou un broker MQTT font à l'échelle d'un réseau.

### 21.3 Les jalons

Ne commence pas par l'API. Commence par ce qui se teste dans le REPL sans rien lancer, et remonte.

1. **Modèles, base, configuration.** `models.py`, `db.py`, `config.py`. Objectif : dans un `python3 -i`, créer une cible, lui attacher deux `Check`, et obtenir son état avec `status_of()`. Pas une ligne de FastAPI.
2. **Vérifications.** `checks.py` : trois coroutines et un aiguillage `run_check()`. Teste avec `asyncio.run(check_http("http://localhost:8000"))` contre un `python3 -m http.server`. Le ping se teste sur `127.0.0.1`.
3. **Bus et worker.** `bus.py`, `worker.py`. Un `tick()` que tu peux appeler à la main dans un test, une `boucle()` qui l'appelle en continu. Teste que deux cibles sont vérifiées en parallèle (mesure le temps : deux vérifications d'une seconde chacune doivent prendre une seconde, pas deux).
4. **API.** `auth.py` puis `api.py`. Ouvre `/docs`, clique sur *Authorize*, crée une cible, lance une vérification, regarde `/status`. Puis `curl -N localhost:8000/events` dans un second terminal pendant que le worker tourne.
5. **CLI et tests.** `cli.py`, puis fais passer tous les tests fournis. Ils sont écrits : c'est du développement guidé par les tests à l'envers, la spécification est dans `tests/`.
6. **Docker.** `Dockerfile`, `docker-compose.yml`, un volume pour la base. `docker compose up --build`, et la CLI de ta machine ne voit plus la base du conteneur : c'est normal, et c'est l'occasion de réfléchir à ce que ça implique.

### 21.4 Les pièges que tu vas rencontrer

Ils sont listés parce que chacun coûte une heure si on ne sait pas qu'il existe.

- **`get_settings()` est mémorisé.** Avec `lru_cache`, la configuration est lue une fois. Dans les tests, les variables d'environnement doivent être posées *avant* le premier import de `statusboard`. Le `conftest.py` fourni le fait ; regarde comment, et pourquoi il y a des `# noqa: E402`.
- **SQLite en mémoire et les threads.** `sqlite://` crée une base *par connexion*. Le TestClient exécute l'application dans un autre thread que le test : sans `StaticPool`, ton test crée la table dans une base et l'application en cherche une autre. Le message est « no such table », et il n'aide pas.
- **Le TestClient attend la fin de la réponse.** Un flux SSE n'a pas de fin. Tester `/events` avec le TestClient bloque à jamais. La solution est un paramètre `limit` qui ferme le flux après N événements : utile aussi pour `curl` et les scripts.
- **`datetime` et les fuseaux.** Tu écris des datetimes en UTC avec fuseau, SQLite te les rend *naïfs* (sans fuseau). Comparer les deux lève `TypeError: can't compare offset-naive and offset-aware datetimes`. Remets le fuseau à la lecture.
- **`asyncio.gather` et les exceptions.** Par défaut, la première exception fait tomber tout le `gather`. Chaque vérification doit attraper ses propres erreurs et renvoyer un `Check` en échec plutôt que de lever. Une cible injoignable est un résultat, pas une panne du worker.
- **Annuler une tâche.** `tache.cancel()` ne l'arrête pas : ça programme une `CancelledError` à son prochain `await`. Il faut ensuite `await tache` (dans un `suppress(CancelledError)`) pour qu'elle finisse vraiment, sinon uvicorn se plaint d'une tâche détruite en attente.
- **bcrypt et passlib.** La surcouche `passlib`, encore citée partout, ne suit plus les versions récentes de `bcrypt` et échoue au premier hachage. Appelle `bcrypt` directement : deux fonctions, `hashpw` et `checkpw`.
- **`ping` n'est pas dans l'image Docker slim.** `apt-get install iputils-ping`, sinon ta vérification ping renvoie « commande absente » en production et rien d'autre.

### 21.5 Quand est-ce que c'est fini

- `pytest` vert, `ruff check .` vide, le paquet s'installe avec `pip install .`.
- Une cible qui passe de UP à DOWN apparaît dans `curl -N /events` avec `"changed": true` avant la fin de son intervalle.
- L'API refuse un POST sans jeton (401), un doublon (409), une cible inconnue (404).
- Le conteneur tourne en non-root et la base survit à un `docker compose down` puis `up`.

Si tout ça est vrai, tu as écrit une application Python complète : async, base de données, API authentifiée, temps réel, CLI, tests, conteneur. Ce n'est plus du Python de script. Compare avec ce que tu aurais écrit au chapitre 3.

### 21.6 Où lire ensuite

- **La documentation officielle** ([docs.python.org](https://docs.python.org/3/)) : le tutoriel est moyen, mais la *Library Reference* est excellente et c'est là qu'il faut aller pour `asyncio`, `logging`, `pathlib`, `dataclasses`. Le *What's New* de chaque version, une fois par an, vaut vingt minutes.
- **Fluent Python** (Luciano Ramalho, 2e édition) : le livre qui explique *pourquoi* Python est comme il est. Modèle de données, itérateurs, décorateurs, async, métaclasses. Long, dense, indispensable après ce cours.
- **Real Python** ([realpython.com](https://realpython.com)) : des articles longs et sérieux sur un sujet à la fois. Quand tu tombes sur un concept que tu n'as pas vu ici, cherche-le là d'abord.
- **Python Morsels** (Trey Hunner) : un exercice par semaine, avec correction détaillée. Pour entretenir.
- **Les talks** : Raymond Hettinger (*Beyond PEP 8*, *Transforming Code into Beautiful, Idiomatic Python*), David Beazley (tout ce qu'il a fait sur les générateurs et la concurrence), Brandon Rhodes (*The Dictionary Even Mightier*). Ce sont des cours en une heure.
- **La PEP 8** et **la PEP 20** (`python3 -m this`) : à relire une fois par an.

### 21.7 Ce que le cours n'a pas couvert

Deux lignes par sujet, pour savoir que ça existe et par où commencer.

- **numpy et pandas** : les tableaux numériques et les tables de données. Tout le calcul scientifique et la data en Python passe par là ; numpy est du C avec une interface Python, cent fois plus rapide qu'une boucle sur des listes. Commence par pandas si tu traites des CSV ou des exports de monitoring.
- **Django** : le framework web complet, avec ORM, admin, authentification, formulaires, tout inclus. Le choix quand il faut un site avec des pages, des utilisateurs et un back-office, pas seulement une API. Plus lourd que FastAPI, mais tu ne réécris rien.
- **Flask** : l'ancêtre minimaliste de FastAPI, synchrone. Encore partout dans les projets existants ; si tu tombes dessus, tout ce que tu sais de FastAPI se transpose.
- **Celery et RQ** : des files de tâches distribuées, avec Redis ou RabbitMQ comme transport. Quand le worker du chapitre 21 ne suffit plus : plusieurs machines, des tâches longues, des reprises sur erreur, une planification.
- **Ansible en Python** : Ansible *est* du Python. Un module Ansible est un script Python qui lit du JSON et en renvoie ; un plugin de filtre est une fonction. Tu peux étendre l'outil que tu utilises déjà.
- **boto3 et les SDK cloud** : chaque cloud a son SDK Python (boto3 pour AWS, `google-cloud-*`, `azure-*`). Même modèle partout : un client, des méthodes qui appellent l'API REST, des paginateurs. Le chapitre 14 t'a préparé.
- **Scraping** : `httpx` + `BeautifulSoup` pour du HTML statique, `playwright` pour piloter un vrai navigateur. Regarde les conditions d'utilisation avant.
- **Textual** : des interfaces en mode texte, riches, dans le terminal, avec le modèle d'événements et le CSS d'une application web. Par les auteurs de `rich`. Pour un tableau de bord SSH.
- **Extensions natives** : quand une fonction est trop lente, on l'écrit en C (`ctypes`, `cffi`, l'API C de CPython) ou, aujourd'hui, en Rust avec **PyO3** et `maturin`. C'est comme ça que ruff, uv, pydantic-core et polars sont faits.
- **Machine learning** : scikit-learn pour les modèles classiques, PyTorch pour les réseaux de neurones, Hugging Face pour les modèles pré-entraînés. Le Python est simple ; c'est la méthode qui prend du temps.
- **Le GIL, suite** : Python 3.13 a un mode expérimental sans GIL (*free-threaded*, `python3.13t`) et 3.14 le consolide. Le chapitre 10 devient un chapitre d'histoire, lentement.

### 21.8 Continuer en DevOps avec Python

Trois projets réalistes, dans l'ordre de difficulté, pour faire de Python ton outil d'infra plutôt qu'un langage de cours.

**Un module Ansible.** Un fichier Python dans `library/`, une classe `AnsibleModule` qui déclare ses arguments, une fonction qui fait le travail de façon idempotente et renvoie `changed=True/False`. Écris-en un pour quelque chose que tu fais aujourd'hui en `shell:` avec des `when:` fragiles. Documentation : *Developing modules* dans les docs Ansible.

**Un exporteur Prometheus.** Le paquet `prometheus_client` expose un `/metrics` en dix lignes. Reprends le statusboard et ajoute `statusboard_up{target="…"}` et `statusboard_latency_ms`. Grafana dessus, et tu as un tableau de bord d'astreinte. C'est le format que tout ton monitoring parle ; savoir l'émettre depuis n'importe quel script est une compétence qui sert chaque semaine.

**Un opérateur Kubernetes.** Le framework `kopf` transforme des fonctions Python décorées en opérateur : `@kopf.on.create("statusboard.stranix.net", "v1", "targets")` et ta fonction est appelée quand quelqu'un applique une ressource personnalisée. C'est la façon Python d'étendre Kubernetes, plus accessible que Go pour un premier opérateur, et ça te fera comprendre le modèle de réconciliation mieux que n'importe quel article.

Et le fil qui relie les trois : ce que tu fais en shell avec des `grep | awk | sed` chaînés et des variables non quotées, écris-le en Python dès que ça dépasse dix lignes ou que ça doit gérer une erreur. Le chapitre 13 t'a donné la trousse. `subprocess`, `pathlib`, `json`, `argparse`, `logging` : c'est du shell qui ne casse pas au premier espace dans un nom de fichier.

### 21.9 Ce qu'il faut retenir

- Un projet complet se construit du bas vers le haut : modèles, logique, worker, API, CLI, livraison. L'API en dernier, pas en premier.
- Le worker dans le processus de l'API, une session courte autour de chaque `await` long, une `Queue` par abonné : trois patrons qui tiennent jusqu'à ce qu'on ait besoin de Redis.
- Les tests fournis sont la spécification. Les faire passer, c'est finir.
- Ce que tu ne sais pas encore (numpy, Django, Celery, kopf…) se construit sur ce que tu sais maintenant : la syntaxe, les itérateurs, l'async, HTTP, les tests, l'empaquetage.

**Labo 21** : le statusboard, en six jalons, avec les tests fournis et une solution complète à ne regarder qu'après.

---

← [20. Qualité, empaquetage, déploiement](20-qualite-empaqueter-deployer.md) · [Sommaire](../README.md)
