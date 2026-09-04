# src/statusboard/api.py — Labo 21 : l'application FastAPI (jalon 4).
"""API REST + SSE de statusboard."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from statusboard.bus import bus


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # TODO : init_db(), assurer_admin(), lancer worker.boucle() en tâche de fond si
    #        get_settings().worker_enabled ; après le yield, annuler la tâche et l'attendre.
    yield


app = FastAPI(title="statusboard", version="0.1.0", lifespan=lifespan)

# TODO : POST /token, GET/POST /targets, DELETE /targets/{id}, GET /targets/{id}/checks,
#        POST /targets/{id}/check, GET /status, GET /events (StreamingResponse text/event-stream,
#        paramètre limit pour fermer après N événements : TestClient ne sait pas lire un flux infini).


@app.get("/health")
def health() -> dict[str, str | int]:
    return {"status": "ok", "sse_clients": bus.nb_abonnes}
