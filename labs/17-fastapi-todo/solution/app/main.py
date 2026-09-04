# app/main.py — Labo 17 : point d'entrée de l'API. C'est ce fichier que uvicorn charge :
#     uvicorn app.main:app --reload
# « app.main » = le module, « :app » = la variable FastAPI dedans.
#
# Rôle : créer l'application, brancher les routeurs, exposer / et /health.

from fastapi import FastAPI

from . import store
from .routers import tickets

# title/description/version apparaissent en tête de /docs et dans openapi.json.
app = FastAPI(
    title="Tickets d'incidents",
    description="Labo 17 du cours Python : une API CRUD en mémoire.",
    version="0.1.0",
)

# Toutes les routes définies dans routers/tickets.py sont maintenant servies
# sous /tickets (le prefix est dans le routeur lui-même).
app.include_router(tickets.router)

# Quelques tickets au démarrage, pour que GET /tickets ne renvoie pas [].
store.peupler()


@app.get("/", tags=["meta"])
def racine() -> dict[str, str]:
    # Un dict est converti en JSON automatiquement.
    return {"service": "tickets", "docs": "/docs"}


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    # La route que ton orchestrateur (Docker, Kubernetes, un load balancer)
    # appellera toutes les 10 secondes pour savoir si le service est vivant.
    return {"status": "ok"}
