# Labo 21 — Projet final : statusboard

**Chapitre** : [21. Projet final et pour aller plus loin](../../cours/21-projet-final-et-suite.md)

## Objectif
Construire seul, de bout en bout, un service de surveillance : des cibles HTTP, TCP et ping en base, un worker asynchrone qui les vérifie, une API FastAPI authentifiée, un flux temps réel, une CLI, des tests et un conteneur. Tout ce que le cours a vu, dans un seul projet.

## Cahier des charges
- **Cibles** : nom unique, type (`http`, `tcp`, `ping`), adresse, intervalle en secondes, activée ou non. Stockées en SQLite via SQLModel.
- **Vérifications** : HTTP = GET, OK si statut < 400 ; TCP = connexion à `hôte:port` ; ping = la commande `ping -c 1` du système. Chaque résultat (horodatage, OK/KO, latence, détail) est conservé : c'est l'historique.
- **Worker** : une tâche asyncio lancée avec l'API, qui vérifie en parallèle toutes les cibles dont l'intervalle est écoulé, et publie un événement à chaque résultat.
- **API** : `POST /token` (OAuth2 password → JWT), `GET/POST /targets`, `DELETE /targets/{id}`, `GET /targets/{id}/checks`, `POST /targets/{id}/check` (vérification immédiate), `GET /status` (chaque cible + dernier résultat), `GET /events` (Server-Sent Events : un instantané puis chaque vérification en direct), `GET /health`. Les écritures exigent un jeton ; les lectures sont publiques. `/docs` doit être utilisable.
- **CLI** `statusboard` : `add`, `list`, `status`, `check NOM`, `serve`.
- **Configuration** par variables d'environnement `STATUSBOARD_*` (base, secret, admin, intervalle, worker on/off).
- **Tests** pytest : vérifications contre un serveur HTTP local lancé dans un thread, API via TestClient, un tick du worker à la main, la CLI via `CliRunner`.
- **Livraison** : `Dockerfile` et `docker-compose.yml` avec un volume pour la base.

## Jalons
1. **Modèles et base** (`models.py`, `db.py`, `config.py`) : `Target`, `Check`, `User` ; `init_db()` ; `status_of()` qui renvoie une cible avec son dernier check. Testable dans le REPL avant toute API.
2. **Vérifications** (`checks.py`) : trois coroutines + `run_check(target)`. Teste-les avec `asyncio.run()` contre `python3 -m http.server`.
3. **Worker et bus** (`bus.py`, `worker.py`) : `Broadcaster` avec `subscribe()` en context manager async ; `tick()` qui vérifie les cibles dues avec `asyncio.gather` ; `boucle()` qui tourne jusqu'à annulation.
4. **API** (`auth.py`, `api.py`) : lifespan (tables, admin, worker), routes, SSE. Vérifie dans `/docs` avec le bouton Authorize.
5. **CLI** (`cli.py`) et **tests** : le dossier `tests/` contient un `conftest.py` prêt (serveur local, base en mémoire, client authentifié) et des tests qui échouent tant que le code n'existe pas.
6. **Docker** : `docker compose up --build`, puis `curl -N localhost:8000/events` depuis l'hôte.

## Comment lancer
```bash
source ../../.venv/bin/activate
pip install -e .                 # src/ layout : il faut installer (chapitre 20)
pytest                           # rouge au départ, vert à la fin
statusboard add site http https://stranix.net
statusboard serve                # http://127.0.0.1:8000/docs

cd solution && bash verifier.sh  # lint + tests + lancement réel de la solution
```

Le squelette et la solution ont le même nom de paquet : `pip install -e .` dans l'un remplace l'autre. `pip uninstall statusboard` pour nettoyer.

## Critères « c'est fini »
- `pytest` vert, `ruff check .` vide.
- Une cible qui passe de UP à DOWN apparaît dans `curl -N /events` avec `"changed": true` en moins d'un intervalle.
- L'API refuse un POST sans jeton (401) et un doublon de nom (409).
- Le conteneur tourne en non-root, et la base survit à `docker compose down && docker compose up`.

## Pour aller plus loin
- Remplace SQLite par PostgreSQL (`docker compose` avec un service `db`, `STATUSBOARD_DATABASE_URL=postgresql+psycopg://…`) : combien de lignes changent ?
- Ajoute une page HTML minimale servie par l'API qui écoute `/events` avec `EventSource` et colore les cibles : ton premier tableau de bord temps réel, sans framework.
- Exporte les métriques au format Prometheus (`/metrics` : `statusboard_up{target="site"} 1`) et branche Grafana dessus.
