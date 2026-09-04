# Labo 19 — L'API complète : base SQLite, JWT, rôles, Docker

**Chapitre** : [19. FastAPI avancé : dépendances, auth, tests, Docker](../../cours/19-fastapi-avance.md)

## Objectif
Assembler les labos 17 et 18 en une API qu'on pourrait vraiment déployer : tickets persistants liés à leur auteur, inscription et login par jeton JWT, suppression réservée aux admins, tests avec base en mémoire, et un conteneur Docker.

## Consignes
1. Lis `app/` dans cet ordre : `config.py` (les réglages viennent de l'environnement), `models.py` (une table + ses schémas d'API), `db.py` (la session par requête avec `yield`), `deps.py`, puis les routeurs et `main.py`. Lance `uvicorn app.main:app --reload` : l'app démarre, crée `tickets.db` et le compte `admin`. Ouvre `/docs` : le bouton *Authorize* est là, mais `/auth/token` répond 501.
2. `app/security.py` : écris `creer_token` et `decoder_token` avec PyJWT (`jwt.encode`, `jwt.decode`, attraper `jwt.PyJWTError`). Vérifie dans le REPL : `python3 -c "from app.security import *; t = creer_token('gilles'); print(t); print(decoder_token(t)); print(decoder_token(t + 'x'))"`. Décode le milieu du jeton avec `base64 -d` : le contenu est lisible, seule la signature protège.
3. `app/routers/auth.py` : écris le login (`/auth/token`), avec le même message d'erreur que l'utilisateur existe ou non. Puis `app/deps.py` : `get_current_user` (jeton → `User` en base, 401 sinon, avec l'en-tête `WWW-Authenticate`) et `require_admin` (403). Teste avec *Authorize* dans `/docs`, puis `/auth/me`.
4. `app/routers/tickets.py` : un non-admin ne voit que ses tickets (dans la liste **et** en lecture directe : 404, pas 403, pour ne rien révéler) ; la suppression passe par `AdminUser`. Rejoue le scénario `curl` ci-dessous : il doit donner exactement les codes indiqués.
5. `app/main.py` : ajoute le middleware CORS et complète le middleware `chrono` (en-tête `X-Process-Time` + une ligne de log par requête). `pytest` : 12 tests. Ils prennent quelques secondes : c'est bcrypt, et c'est voulu.
6. `Dockerfile` : utilisateur non-root, `HEALTHCHECK`, `CMD`. Si Docker est installé : `docker compose up --build`, puis le scénario `curl` sur le port 8000, `docker compose down`, `up` à nouveau : les tickets sont toujours là (volume). Bonus : ajoute une route `GET /tickets/stats` réservée aux admins qui compte les tickets par statut (`select(Ticket.statut, func.count())…group_by`).

## Comment lancer
```bash
source ../../.venv/bin/activate
cp .env.example .env                          # optionnel : surcharge les réglages
uvicorn app.main:app --reload                 # http://127.0.0.1:8000/docs
pytest                                        # ton squelette
SOLUTION=1 pytest                             # la solution
cd solution && TICKETS_ADMIN_PASSWORD=admin123 uvicorn app.main:app   # la solution
docker compose up --build                     # si Docker est là
```

Le scénario complet, à la main :

```bash
B=http://127.0.0.1:8000
curl -s $B/health                                     # {"status":"ok","version":"1.0.0"}
curl -s -X POST $B/auth/register -H "Content-Type: application/json" \
     -d '{"username":"gilles","password":"motdepasse1"}'   # 201 {"username":"gilles","id":2,"is_admin":false}
TOKEN=$(curl -s -X POST $B/auth/token -d "username=gilles&password=motdepasse1" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo $TOKEN | cut -d. -f2 | base64 -d                 # {"sub":"gilles","exp":1788527212} : lisible !
curl -s -X POST $B/tickets -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     -d '{"titre":"Disque plein sur srv-db-01","severite":"haute"}'   # 201
curl -s $B/tickets -H "Authorization: Bearer $TOKEN"  # la liste de SES tickets
curl -s -i $B/tickets | head -1                       # HTTP/1.1 401 Unauthorized
curl -s -i -X DELETE $B/tickets/1 -H "Authorization: Bearer $TOKEN" | head -1   # HTTP/1.1 403 Forbidden
ADMIN=$(curl -s -X POST $B/auth/token -d "username=admin&password=admin-a-changer" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
curl -s -i -X DELETE $B/tickets/1 -H "Authorization: Bearer $ADMIN" | head -1   # HTTP/1.1 204 No Content
```

## Pour aller plus loin
- Mets `TICKETS_TOKEN_MINUTES=0` dans `.env`, redémarre, prends un jeton : `/auth/me` répond 401 « expiré ». C'est `exp` qui travaille.
- Change `TICKETS_DATABASE_URL` pour un PostgreSQL (`docker run -e POSTGRES_PASSWORD=x -p 5432:5432 postgres`, `pip install psycopg`, URL `postgresql+psycopg://postgres:x@localhost/postgres`) : rien d'autre à modifier.
- Ajoute un *refresh token* : le jeton d'accès court (15 min) et un second jeton long stocké en base, révocable. C'est ce que font les vraies applications, et c'est l'occasion de voir pourquoi un JWT seul ne se révoque pas.
