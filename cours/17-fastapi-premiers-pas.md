# 17. FastAPI : premiers pas

*Python de zéro à FastAPI — chapitre 17 sur 21.* ← [16. Web services : REST, SOAP, GraphQL, gRPC, WebSocket](16-web-services-panorama.md) · [Sommaire](../README.md) · [18. Bases de données : sqlite3, SQLAlchemy, SQLModel](18-bases-de-donnees.md) →

> 🧪 Labo associé : [`labs/17-fastapi-todo`](../labs/17-fastapi-todo/README.md)

Au chapitre 16, tu as écrit un serveur REST à la main avec `http.server` : parser l'URL, lire le body, valider le JSON, fabriquer la réponse, choisir le code de statut. C'était instructif et pénible. FastAPI fait tout ça pour toi, et en prime il écrit la documentation.

### 17.1 Ce qu'est FastAPI

FastAPI est un *framework* web, sorti en 2018, qui assemble deux briques existantes et une idée :

- **Starlette** : la couche HTTP. Routage, requêtes, réponses, middlewares, WebSocket. C'est elle qui parle au serveur.
- **pydantic** : la couche données. Tu décris la forme d'un objet avec des type hints, pydantic valide, convertit, et sérialise en JSON.
- **L'idée** : les type hints Python (chapitre 5) suffisent à décrire une API. `def lire(ticket_id: int)` dit tout : un paramètre, entier, obligatoire. FastAPI en déduit la conversion, la validation, l'erreur 422 si ce n'est pas un entier, et la ligne correspondante dans la documentation OpenAPI.

Avant lui, il y avait Flask (minimal, tout à la main, synchrone) et Django REST Framework (énorme, lié à Django). FastAPI est devenu le standard pour une API en Python parce qu'il est **asynchrone natif** (chapitre 15), **typé** (ton éditeur te complète tout) et **auto-documenté**. Sa doc officielle, [fastapi.tiangolo.com](https://fastapi.tiangolo.com/fr/), est excellente et en français : ce chapitre est un raccourci, pas un remplaçant.

> **Venant de Java** : Spring Boot avec des annotations `@GetMapping` et des DTO validés par `@Valid`. Les décorateurs de FastAPI jouent le rôle des annotations, les modèles pydantic celui des DTO, et le tout tient en dix fois moins de lignes.

> **ASGI et WSGI** : un framework web Python ne sert pas HTTP lui-même. Il expose une fonction (une « application ») que le **serveur** appelle à chaque requête. L'interface historique s'appelle WSGI (2003, synchrone : une requête, un thread, bloqué jusqu'à la réponse). Flask et Django classique sont WSGI. **ASGI** (2016) est sa version asynchrone : l'application est une coroutine, le serveur peut en faire tourner des milliers en parallèle sur une boucle d'événements, et gérer WebSocket. FastAPI est ASGI. Le serveur ASGI de référence est **uvicorn**.

### 17.2 Le plus petit service du monde

```python
# main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def racine():
    return {"message": "Bonjour"}
```

```bash
uvicorn main:app --reload
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

`main:app` = le module `main`, la variable `app` dedans. `--reload` relance le serveur à chaque sauvegarde (développement seulement). `--host 0.0.0.0 --port 8080` pour écouter sur toutes les interfaces et un autre port, ce qu'il faudra dans Docker.

Trois choses à voir :

1. `@app.get("/")` est un **décorateur** (chapitre 11) : il enregistre `racine` comme la fonction à appeler pour un `GET /`. Il y a `@app.post`, `@app.put`, `@app.patch`, `@app.delete`, un par verbe HTTP du chapitre 14.
2. La fonction renvoie un **dict**, FastAPI le transforme en JSON et met `Content-Type: application/json`. Elle pourrait renvoyer une liste, un modèle pydantic, une chaîne, `None`.
3. Ouvre http://127.0.0.1:8000/docs. Tu as une page **Swagger UI** qui liste ta route, et un bouton *Try it out* qui l'appelle. Tu n'as rien écrit pour ça.

### 17.3 Paramètres de chemin et de requête

```python
@app.get("/serveurs/{nom}")
def serveur(nom: str, verbose: bool = False, lignes: int = 10):
    return {"nom": nom, "verbose": verbose, "lignes": lignes}
```

La règle : un paramètre de la fonction qui apparaît entre accolades dans le chemin est un **paramètre de chemin** ; les autres sont des **paramètres de requête** (après le `?`). Le type hint fait le reste :

| Requête | Réponse |
|---|---|
| `GET /serveurs/web-01` | `{"nom": "web-01", "verbose": false, "lignes": 10}` |
| `GET /serveurs/web-01?verbose=true&lignes=50` | `{"nom": "web-01", "verbose": true, "lignes": 50}` |
| `GET /serveurs/web-01?verbose=yes` | `verbose: true` (`yes`, `on`, `1` sont acceptés) |
| `GET /serveurs/web-01?lignes=beaucoup` | **422** avec le détail ci-dessous |

```json
{"detail": [{"type": "int_parsing", "loc": ["query", "lignes"],
             "msg": "Input should be a valid integer, unable to parse string as an integer",
             "input": "beaucoup"}]}
```

Un paramètre sans valeur par défaut est obligatoire (422 s'il manque). `X | None = None` le rend optionnel. Pour des contraintes, `Query()` :

```python
from fastapi import Query

@app.get("/tickets")
def lister(limite: int = Query(default=100, ge=1, le=1000, description="Nombre max renvoyé")):
    ...
```

`ge`, `le`, `gt`, `lt`, `min_length`, `max_length`, `pattern` (une regex) : tout est vérifié avant que ta fonction ne soit appelée, et tout apparaît dans la doc.

> **Piège** : l'ordre de déclaration compte. Si tu déclares `GET /tickets/{ticket_id}` avant `GET /tickets/stats`, un appel à `/tickets/stats` tombe sur la première route, tente de convertir `"stats"` en `int`, et répond 422. Les routes fixes se déclarent avant les routes à paramètre.

### 17.4 pydantic : décrire les données

Pour un body JSON (POST, PUT, PATCH), on décrit sa forme avec une classe qui hérite de `BaseModel` :

```python
from pydantic import BaseModel, Field

class Serveur(BaseModel):
    nom: str = Field(min_length=2)
    ip: str
    cpu: int = Field(ge=1, le=256)
    tags: list[str] = []
```

Ça ressemble à une `dataclass` (chapitre 9), mais chaque champ est **validé** à la construction :

```python
>>> s = Serveur(nom="web-01", ip="10.0.0.1", cpu=4)
>>> s
Serveur(nom='web-01', ip='10.0.0.1', cpu=4, tags=[])
>>> s.model_dump()                 # → dict
{'nom': 'web-01', 'ip': '10.0.0.1', 'cpu': 4, 'tags': []}
>>> s.model_dump_json()            # → chaîne JSON
'{"nom":"web-01","ip":"10.0.0.1","cpu":4,"tags":[]}'
>>> Serveur(nom="web-01", ip="10.0.0.1", cpu="quatre")
Traceback (most recent call last):
  ...
pydantic_core._pydantic_core.ValidationError: 1 validation error for Serveur
cpu
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='quatre', input_type=str]
```

Et `Serveur(..., cpu="4")` passe : pydantic **convertit** ce qui est convertible sans ambiguïté (`"4"` → `4`), refuse le reste. Ce mode « laxiste » est celui par défaut ; il existe un mode strict. `Serveur.model_validate(un_dict)` construit depuis un dict, et les clés inconnues sont ignorées par défaut.

Les types acceptés : tous les types de base, `datetime`, `Enum`, `list[...]`, `dict[...]`, `X | None`, d'autres modèles imbriqués, et une bibliothèque de types spéciaux (`EmailStr`, `HttpUrl`, `IPvAnyAddress`, …). Pour un champ à valeurs fixes, une `Enum` qui hérite aussi de `str` :

```python
from enum import Enum

class Severite(str, Enum):
    BASSE = "basse"
    HAUTE = "haute"
```

Hériter de `str` fait que la valeur se sérialise en `"haute"` et que Swagger UI propose un menu déroulant.

> **Venant du C** : c'est un `struct` avec les vérifications qu'on n'écrit jamais. La différence de fond : en C, une struct contient des octets et tu espères qu'ils ont du sens ; ici, si l'objet existe, il est valide. On appelle ça *parse, don't validate* : on ne vérifie pas des données brutes un peu partout, on les transforme une fois en un objet qui ne peut pas être faux.

### 17.5 Body, codes de statut, erreurs

```python
from fastapi import HTTPException, status

@app.post("/serveurs", status_code=status.HTTP_201_CREATED, response_model=Serveur)
def creer(s: Serveur):
    if s.nom in INVENTAIRE:
        raise HTTPException(status_code=409, detail=f"{s.nom} existe déjà")
    INVENTAIRE[s.nom] = s
    return s
```

- **Le body** : un paramètre dont le type est un `BaseModel` est lu dans le corps JSON de la requête, validé, et si ça ne va pas, 422 avec le détail par champ. Ta fonction ne voit jamais de données invalides.
- **`status_code=201`** : le code de la réponse en cas de succès. Par défaut 200. `204` pour un DELETE sans corps. Le module `status` donne des noms lisibles, mais `201` marche aussi.
- **`HTTPException`** : la façon de répondre une erreur. On la `raise`, FastAPI l'attrape et renvoie `{"detail": "..."}` avec le code. 404 introuvable, 409 conflit, 403 interdit, 401 non authentifié (chapitre 19).
- **`response_model`** : le modèle de la **réponse**. FastAPI valide ce que tu renvoies, le documente, et surtout **filtre** : si tu renvoies un objet qui a plus de champs que le modèle (un utilisateur avec son mot de passe haché…), seuls ceux du modèle partent. On s'en sert au chapitre 19.

Un modèle par usage est la norme : `TicketCreate` (ce que le client envoie), `Ticket` (ce qu'on stocke et renvoie, avec `id` et `cree_le` en plus), `TicketUpdate` (tout optionnel, pour le PATCH). L'héritage évite de répéter les champs : `class Ticket(TicketCreate): id: int`.

Pour un PATCH, le bon réflexe :

```python
changements = donnees.model_dump(exclude_unset=True)   # seulement les champs envoyés
nouveau = ancien.model_copy(update=changements)
```

Sans `exclude_unset`, un `PATCH {"statut": "resolu"}` mettrait `titre` à `None`.

### 17.6 La doc, et le contrat OpenAPI

Trois URLs existent dès que l'app démarre :

| URL | Quoi |
|---|---|
| `/docs` | Swagger UI : la doc interactive, avec *Try it out* |
| `/redoc` | La même doc, présentation ReDoc, plus lisible, non interactive |
| `/openapi.json` | Le **contrat** OpenAPI (chapitre 16) : routes, paramètres, modèles, codes, en JSON |

Ce fichier JSON est généré depuis tes signatures et tes modèles. C'est ce qu'un collègue donne à son générateur de client (TypeScript, Java, Go…), ce que Postman importe, ce qu'un `curl` humain lit pour savoir quoi envoyer. Tu ne maintiens pas de documentation à part : elle **est** le code. `FastAPI(title=..., description=..., version=...)` remplit l'en-tête, `tags=["tickets"]` sur une route la range dans une section, la docstring de la fonction devient sa description.

### 17.7 `async def` ou `def` ?

```python
@app.get("/a")
def sync_route():          # tourne dans un thread du pool
    ...

@app.get("/b")
async def async_route():   # tourne sur la boucle d'événements
    ...
```

Les deux marchent. La règle (chapitre 15) : `async def` si tout ce que tu attends dedans est `await`-able (httpx async, une BDD async) ; `def` si tu appelles du code bloquant (`requests`, `sqlite3`, `time.sleep`, un calcul lourd). FastAPI exécute une route `def` dans un thread séparé pour ne pas bloquer la boucle, donc un `def` honnête vaut mieux qu'un `async def` qui bloque. Dans ce cours, `sqlite3` et SQLModel sont synchrones : routes en `def`.

### 17.8 Organiser : `APIRouter`

Un `main.py` de 2000 lignes n'est pas une option. Le découpage standard :

```
app/
├── __init__.py
├── main.py          # crée l'app, branche les routeurs
├── models.py        # pydantic
├── store.py         # accès aux données
└── routers/
    ├── __init__.py
    ├── tickets.py   # router = APIRouter(prefix="/tickets", tags=["tickets"])
    └── users.py
```

```python
# app/routers/tickets.py
from fastapi import APIRouter
router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.get("")
def lister(): ...

# app/main.py
from .routers import tickets
app = FastAPI(title="Tickets")
app.include_router(tickets.router)
```

Un `APIRouter` se déclare comme une app, se branche avec `include_router`. Tout ce qu'il contient hérite du préfixe et des tags. On lance avec `uvicorn app.main:app`.

### 17.9 Tester sans serveur

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_creer():
    r = client.post("/tickets", json={"titre": "Disque plein", "severite": "haute"})
    assert r.status_code == 201
    assert r.json()["statut"] == "ouvert"
```

`TestClient` (basé sur httpx) appelle l'application ASGI **directement**, sans réseau, sans uvicorn. Même API que httpx du chapitre 14 : `.get()`, `.post(json=...)`, `.status_code`, `.json()`. C'est rapide (des centaines de tests par seconde), et ça se lance avec `pytest` comme au chapitre 12. On teste ainsi les cas heureux, les 404, les 422, les filtres.

À la main, `curl` reste l'outil universel :

```bash
curl -s localhost:8000/tickets | python3 -m json.tool
curl -s -X POST localhost:8000/tickets -H "Content-Type: application/json" \
     -d '{"titre":"Réseau HS","severite":"critique"}'
curl -s -i -X DELETE localhost:8000/tickets/4 | head -1
```

Et [httpie](https://httpie.io) (`pip install httpie`) est le même outil en lisible : `http POST :8000/tickets titre="Réseau HS" severite=critique`.

### 17.10 Ce qu'il faut retenir

- FastAPI = Starlette (HTTP, ASGI) + pydantic (données) + type hints. Serveur : uvicorn.
- Un décorateur par route ; les paramètres de chemin sont entre accolades, les autres sont des paramètres de requête ; le type hint fait conversion, validation, 422 et doc.
- Un `BaseModel` par usage (`Create`, `Update`, réponse). Si l'objet existe, il est valide.
- `status_code` pour le succès, `raise HTTPException` pour l'erreur, `response_model` pour filtrer et documenter la réponse.
- `/docs`, `/redoc`, `/openapi.json` viennent gratuitement : la doc est le code.
- `APIRouter` pour découper, `TestClient` pour tester sans serveur.

**Labo 17** : une API de tickets d'incidents, CRUD complet en mémoire, en paquet avec routeur, testée avec `TestClient`.

---

← [16. Web services : REST, SOAP, GraphQL, gRPC, WebSocket](16-web-services-panorama.md) · [Sommaire](../README.md) · [18. Bases de données : sqlite3, SQLAlchemy, SQLModel](18-bases-de-donnees.md) →
