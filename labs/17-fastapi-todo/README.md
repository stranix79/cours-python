# Labo 17 — Une API de tickets d'incidents avec FastAPI

**Chapitre** : [17. FastAPI : premiers pas](../../cours/17-fastapi-premiers-pas.md)

## Objectif
Construire une API REST complète (CRUD) avec FastAPI et pydantic, découpée en paquet `app/` avec un routeur, testée avec `TestClient` sans lancer de serveur.

## Consignes
1. Lance le squelette : `uvicorn app.main:app --reload`, ouvre http://127.0.0.1:8000/docs. Deux routes existent déjà (`GET /tickets`, `GET /tickets/{id}`), les quatre autres répondent `501 Not Implemented`. Essaie-les depuis Swagger UI.
2. Dans `app/models.py`, complète `TicketUpdate` : les mêmes champs que `TicketReplace`, tous optionnels (`X | None = None`).
3. Dans `app/routers/tickets.py`, écris `POST /tickets` (201, body `TicketCreate`, `store.creer`) et ajoute le filtre `severite` au `GET /tickets`. Vérifie avec `curl` (bloc plus bas) : un titre de deux lettres ou une sévérité inconnue doivent donner un 422 détaillé sans que tu aies écrit une seule ligne de validation.
4. Écris `PUT` (remplacement complet, on ne garde que `id` et `cree_le`), `PATCH` (modification partielle : `model_dump(exclude_unset=True)` puis `model_copy(update=...)`) et `DELETE` (204 sans corps, 404 si inexistant).
5. `pytest` doit passer les 10 tests. Regarde `/openapi.json` : c'est le contrat de ton API, généré depuis tes types.
6. Bonus : ajoute une route `GET /tickets/stats` qui renvoie `{"ouvert": n, "en_cours": n, "resolu": n}`. Attention à l'ordre de déclaration par rapport à `GET /tickets/{ticket_id}` : pourquoi ?

## Comment lancer
```bash
source ../../.venv/bin/activate
uvicorn app.main:app --reload            # http://127.0.0.1:8000/docs
pytest                                   # teste ton squelette
SOLUTION=1 pytest                        # teste la solution
cd solution && uvicorn app.main:app      # lance la solution
```

Quelques requêtes à la main :

```bash
curl -s localhost:8000/tickets | python3 -m json.tool
curl -s -X POST localhost:8000/tickets -H "Content-Type: application/json" \
     -d '{"titre":"Réseau HS en salle B","severite":"critique"}'
curl -s -X PATCH localhost:8000/tickets/4 -H "Content-Type: application/json" \
     -d '{"statut":"en_cours"}'
curl -s -i -X DELETE localhost:8000/tickets/4 | head -1     # HTTP/1.1 204 No Content
curl -s localhost:8000/tickets/abc                          # 422 : pas un entier
```

## Pour aller plus loin
- Remplace le dict par la base SQLite du labo 18 : c'est exactement ce que fait le labo 19.
- Lance deux workers (`uvicorn app.main:app --workers 2`) et crée un ticket, puis liste plusieurs fois : tu ne le vois qu'une fois sur deux. C'est la démonstration que l'état en mémoire ne survit pas à la mise à l'échelle.
- Installe `httpie` (`pip install httpie`) : `http POST :8000/tickets titre="Test" severite=haute` est plus lisible que `curl` pour ce genre de bricolage.
