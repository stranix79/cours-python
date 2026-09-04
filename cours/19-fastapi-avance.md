# 19. FastAPI avancé : dépendances, auth, tests, Docker

*Python de zéro à FastAPI — chapitre 19 sur 21.* ← [18. Bases de données : sqlite3, SQLAlchemy, SQLModel](18-bases-de-donnees.md) · [Sommaire](../README.md) · [20. Qualité, empaquetage, déploiement](20-qualite-empaqueter-deployer.md) →

> 🧪 Labo associé : [`labs/19-api-complete`](../labs/19-api-complete/README.md)

Le labo 17 est une API jouet : pas de base, pas d'utilisateurs, n'importe qui supprime n'importe quoi. Ce chapitre ajoute tout ce qui sépare un exercice d'un service qu'on met derrière un nom de domaine : la base du chapitre 18, l'authentification, les rôles, la configuration par l'environnement, les tests de bout en bout, et le conteneur.

### 19.1 L'injection de dépendances : `Depends`

Presque chaque route a besoin des mêmes choses : une session de base de données, l'utilisateur qui appelle, des paramètres de pagination. Plutôt que de le répéter, on l'écrit une fois dans une fonction et on demande à FastAPI de l'appeler pour nous :

```python
from collections.abc import Iterator
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session

def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session           # avant : ouvrir ; après la réponse : fermer

SessionDep = Annotated[Session, Depends(get_session)]

@router.get("/tickets")
def lister(session: SessionDep):
    return session.exec(select(Ticket)).all()
```

`Depends(get_session)` dit : « avant d'appeler `lister`, appelle `get_session` et passe le résultat en paramètre ». `Annotated[Type, Depends(...)]` colle le type (pour l'éditeur) et la dépendance (pour FastAPI) dans un alias réutilisable.

Le `yield` est le point important : c'est un générateur (chapitre 11) utilisé comme context manager. Ce qui est avant le `yield` s'exécute avant la route, ce qui est après s'exécute une fois la réponse envoyée, exception ou pas. La session est **toujours** fermée, et il y en a une par requête.

Une dépendance peut dépendre d'une autre (l'utilisateur courant dépend du jeton et de la session), être une classe (FastAPI lit ses paramètres de constructeur dans la requête), ou ne rien renvoyer et juste vérifier quelque chose (un rôle, un quota). C'est le mécanisme central de FastAPI : tout ce qui est transversal passe par là.

> **Venant de Java** : c'est l'`@Autowired` de Spring, sauf que la portée est la requête, que c'est explicite dans la signature, et qu'on peut remplacer n'importe quelle dépendance dans les tests avec `app.dependency_overrides`.

### 19.2 Brancher SQLModel

```python
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)    # au démarrage
    yield
    # à l'arrêt : fermer un pool, vider un cache...

app = FastAPI(lifespan=lifespan)
```

Le **lifespan** est le même motif « avant / `yield` / après », à l'échelle de l'application. `check_same_thread=False` est nécessaire avec SQLite parce que FastAPI exécute les routes `def` dans un pool de threads et que SQLite, par défaut, refuse qu'une connexion change de thread.

Les modèles suivent un découpage standard qui évite de renvoyer un mot de passe haché par accident :

```python
class UserBase(SQLModel):                      # champs communs, pas une table
    username: str = Field(min_length=3, index=True, unique=True)

class User(UserBase, table=True):              # la table
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    is_admin: bool = False

class UserCreate(UserBase):                    # ce que l'API reçoit
    password: str = Field(min_length=8)

class UserPublic(UserBase):                    # ce que l'API renvoie
    id: int
    is_admin: bool
```

Une route `@router.post("/register", response_model=UserPublic)` peut renvoyer l'objet `User` complet : `response_model` ne laisse passer que les champs de `UserPublic`. Pour construire un objet table depuis un schéma d'API en ajoutant ce que le client ne choisit pas : `Ticket.model_validate(donnees, update={"owner_id": user.id})`. Pour appliquer un PATCH : `ticket.sqlmodel_update(donnees.model_dump(exclude_unset=True))`.

> **Piège** : `cree_le: datetime = Field(default_factory=maintenant)`, pas `default=datetime.now()`. Avec `default=`, l'expression est évaluée **une fois**, à l'import du module, et tous les tickets ont la date de démarrage du serveur. Même piège que les arguments par défaut mutables du chapitre 5.

### 19.3 Mots de passe : hacher, jamais stocker

On ne stocke jamais un mot de passe. On stocke un **hachage** : une fonction à sens unique, dont on ne peut pas retrouver l'entrée, mais qu'on peut recalculer pour comparer. Et pas n'importe laquelle : md5 ou sha1 seuls se calculent des milliards de fois par seconde sur un GPU, ce qui rend une base volée cassable en heures. Les fonctions faites pour ça (**bcrypt**, scrypt, argon2) sont **lentes exprès**, environ 100 ms, et **salées** : un aléa par utilisateur, mélangé au hachage, donc deux personnes avec le même mot de passe ont des hachages différents et les tables précalculées ne servent à rien.

```python
import bcrypt

def hacher(mot_de_passe: str) -> str:
    return bcrypt.hashpw(mot_de_passe.encode(), bcrypt.gensalt()).decode()

def verifier(mot_de_passe: str, hachage: str) -> bool:
    return bcrypt.checkpw(mot_de_passe.encode(), hachage.encode())
```

```python
>>> h = hacher("motdepasse1")
>>> h
'$2b$12$K9mE.../…'          # $2b$ = bcrypt, 12 = coût (2^12 itérations), puis sel + hachage
>>> verifier("motdepasse1", h), verifier("faux", h)
(True, False)
```

bcrypt limite l'entrée à 72 octets : on le reflète dans le schéma (`max_length=72`). Si tu croises `passlib` dans un tutoriel, sache qu'il n'est plus maintenu et casse avec les bcrypt récents ; le paquet `bcrypt` seul suffit.

### 19.4 OAuth2 « password flow » et JWT

Le schéma d'authentification le plus courant pour une API :

1. Le client envoie `username` + `password` à `POST /auth/token`, sous forme de **formulaire** (c'est le standard OAuth2, d'où `python-multipart` dans les dépendances).
2. Le serveur vérifie, et renvoie un **jeton** (*token*).
3. Pour chaque requête suivante, le client met `Authorization: Bearer <jeton>` dans l'en-tête. Le serveur vérifie le jeton, sans retoucher au mot de passe.

FastAPI fournit les deux moitiés :

```python
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")   # lit l'en-tête Authorization, 401 s'il manque

@router.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep) -> Token:
    user = session.exec(select(User).where(User.username == form.username)).first()
    if user is None or not verifier(form.password, user.hashed_password):
        raise HTTPException(401, "Nom d'utilisateur ou mot de passe incorrect", headers={"WWW-Authenticate": "Bearer"})
    return Token(access_token=creer_token(user.username))
```

Même message d'erreur que le compte existe ou non : on ne révèle pas la liste des utilisateurs. Et `OAuth2PasswordBearer` a un bonus : il déclare le schéma de sécurité dans OpenAPI, ce qui fait apparaître le bouton *Authorize* dans `/docs`.

Le jeton est un **JWT** (*JSON Web Token*) : trois blocs base64 séparés par des points, `header.payload.signature`.

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnaWxsZXMiLCJleHAiOjE3ODg1MjcyMTJ9.Xk3…
```

```bash
$ echo "$TOKEN" | cut -d. -f2 | base64 -d
{"sub":"gilles","exp":1788527212}
```

Le contenu est **lisible par tous** : ce n'est pas chiffré, c'est signé. La signature est un HMAC-SHA256 du header et du payload avec un secret que seul le serveur connaît. Si quelqu'un modifie `sub`, la signature ne correspond plus, et le jeton est refusé. Conséquences : rien de confidentiel dans le payload ; `exp` (expiration) obligatoire, parce qu'un JWT volé est valable jusqu'à sa date de fin, on ne peut pas le « révoquer » sans garder une liste noire côté serveur ; et le secret est **long** (32 octets minimum : `python3 -c "import secrets; print(secrets.token_hex(32))"`) et vient de l'environnement, jamais du code.

```python
import jwt   # PyJWT

def creer_token(sujet: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.token_minutes)
    return jwt.encode({"sub": sujet, "exp": exp}, settings.secret_key, algorithm="HS256")

def decoder_token(token: str) -> str | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])["sub"]
    except jwt.PyJWTError:          # expiré, signature fausse, malformé
        return None
```

`jwt.decode` vérifie la signature **et** `exp`. Toujours passer `algorithms=[...]` explicitement : une vieille attaque consistait à envoyer un jeton avec `"alg": "none"`.

### 19.5 Utilisateur courant, rôles : 401 contre 403

```python
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep) -> User:
    username = decoder_token(token)
    if username is None:
        raise HTTPException(401, "Jeton invalide ou expiré", headers={"WWW-Authenticate": "Bearer"})
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(401, "Utilisateur inconnu")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

def require_admin(user: CurrentUser) -> User:
    if not user.is_admin:
        raise HTTPException(403, "Réservé aux administrateurs")
    return user

AdminUser = Annotated[User, Depends(require_admin)]
```

Une route protégée demande simplement `user: CurrentUser` ; une route admin, `admin: AdminUser`. Si la dépendance lève, la fonction de route n'est jamais appelée.

| Code | Sens | Quand |
|---|---|---|
| **401** Unauthorized | « je ne sais pas qui tu es » | pas de jeton, jeton invalide ou expiré, mauvais mot de passe |
| **403** Forbidden | « je sais qui tu es, et tu n'as pas le droit » | authentifié mais pas admin |
| **404** Not Found | « ça n'existe pas » | aussi pour la ressource d'un autre utilisateur : on ne confirme même pas qu'elle existe |

### 19.6 Configuration : tout vient de l'environnement

Un secret, une URL de base, une durée de jeton n'ont rien à faire dans le code : ils changent entre ta machine, la préprod et la prod. La règle (les *12 factors*) : tout par variables d'environnement. `pydantic-settings` les lit, les valide et les convertit :

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TICKETS_", env_file=".env")
    secret_key: str = "dev-secret-a-changer"
    database_url: str = "sqlite:///tickets.db"
    token_minutes: int = 60

settings = Settings()      # TICKETS_TOKEN_MINUTES=120 dans l'environnement → settings.token_minutes == 120
```

Un fichier `.env` (gitignoré) sert en développement ; en prod, c'est Docker, systemd ou l'orchestrateur qui injecte les variables. Sans `pydantic-settings`, `os.environ.get("TICKETS_SECRET_KEY", "défaut")` fait le travail, sans la validation.

### 19.7 CORS, middlewares, erreurs globales

**CORS.** Un navigateur qui affiche une page servie par `http://localhost:5173` refuse d'appeler `http://localhost:8000` sauf si ce dernier l'y autorise par des en-têtes `Access-Control-Allow-*`. C'est une protection du navigateur (pas de `curl`, pas d'un autre serveur), et il faut la configurer dès qu'un front web appelle ton API :

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
```

**Middleware.** Une fonction qui voit toutes les requêtes, avant et après la route. Pour un chrono, un id de corrélation, une métrique :

```python
@app.middleware("http")
async def chrono(request: Request, call_next):
    debut = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{(time.perf_counter() - debut) * 1000:.1f}ms"
    return response
```

**Gestionnaire d'erreurs global.** Plutôt qu'attraper `IntegrityError` dans chaque route, une fois pour toutes :

```python
@app.exception_handler(IntegrityError)
async def integrity_error(request, exc):
    return JSONResponse(status_code=409, content={"detail": "Conflit : cette valeur existe déjà"})
```

### 19.8 Tester une API avec base et authentification

Le principe : une base SQLite **en mémoire**, neuve pour chaque test, injectée à la place de la vraie grâce à `dependency_overrides`.

```python
@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    bootstrap_admin(engine)

    def session_de_test():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = session_de_test
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_supprimer_reserve_aux_admins(client, gilles, admin):
    client.post("/tickets", json={"titre": "À supprimer"}, headers=gilles)
    assert client.delete("/tickets/1").status_code == 401
    assert client.delete("/tickets/1", headers=gilles).status_code == 403
    assert client.delete("/tickets/1", headers=admin).status_code == 204
```

`StaticPool` force une seule connexion : une base `:memory:` est *par connexion*, et sans lui chaque thread verrait une base vide différente. Les fixtures `gilles` et `admin` font l'inscription et le login, et renvoient l'en-tête `Authorization` prêt à l'emploi. On teste ainsi les vrais chemins : 401 sans jeton, 403 sans rôle, isolation entre utilisateurs, expiration.

### 19.9 Docker

```dockerfile
FROM python:3.13-slim AS builder
WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim
RUN useradd --create-home --uid 1000 api
WORKDIR /home/api
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1 TICKETS_DATABASE_URL=sqlite:////data/tickets.db
COPY --chown=api:api app ./app
RUN mkdir -p /data && chown api:api /data
USER api
EXPOSE 8000
HEALTHCHECK --interval=30s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
```

Les choix, dans l'ordre : **multi-stage** (l'image finale n'a ni pip ni compilateur) ; **`requirements.txt` copié seul avant le code** (la couche d'installation reste en cache tant que les dépendances ne changent pas) ; **utilisateur non-root** ; **`PYTHONUNBUFFERED=1`** (les logs sortent immédiatement, sinon Docker ne les voit qu'au remplissage du tampon) ; **`--host 0.0.0.0`** (127.0.0.1 dans un conteneur n'est joignable que par le conteneur) ; **`HEALTHCHECK`** sur `/health` ; **la base sur un volume** (`docker-compose.yml` monte `tickets-data:/data`), sinon elle disparaît avec le conteneur.

En production, uvicorn ne fait pas face à Internet tout seul : un **reverse proxy** (nginx, traefik, Caddy) devant lui termine le HTTPS, sert les fichiers statiques et fait le rate-limit. `--proxy-headers` fait confiance à ses en-têtes `X-Forwarded-*` pour connaître le vrai client et le vrai schéma. Pour utiliser tous les cœurs, `--workers 4` (des processus séparés, donc plus d'état en mémoire partagé, une raison de plus d'avoir une base), et des logs en JSON pour ton agrégateur. Le chapitre 20 reprend l'empaquetage et la CI.

### 19.10 Ce qu'il faut retenir

- `Depends` injecte session, utilisateur, pagination ; `yield` garantit le nettoyage ; `dependency_overrides` remplace tout dans les tests.
- Un modèle table + des schémas `Create` / `Update` / `Public` ; `response_model` empêche les fuites.
- Mots de passe : bcrypt, salé, lent exprès. Jamais en clair, jamais md5/sha1.
- JWT : signé, pas chiffré ; `exp` obligatoire ; secret long, dans l'environnement ; `algorithms=[...]` explicite.
- 401 = pas identifié, 403 = identifié sans droit, 404 = pour ne rien révéler.
- Config par variables d'environnement, CORS pour les navigateurs, middleware pour le transversal.
- Docker : multi-stage, non-root, `0.0.0.0`, healthcheck, volume pour la base, reverse proxy devant.

**Labo 19** : l'API de tickets complète, avec base, inscription, login JWT, rôles, tests et conteneur.

---

← [18. Bases de données : sqlite3, SQLAlchemy, SQLModel](18-bases-de-donnees.md) · [Sommaire](../README.md) · [20. Qualité, empaquetage, déploiement](20-qualite-empaqueter-deployer.md) →
