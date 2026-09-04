# src/statusboard/bus.py — Labo 21 (solution) : diffusion d'événements aux clients SSE.
#
# Rôle : le worker publie, chaque client connecté à /events a sa file d'attente
# (asyncio.Queue) et reçoit une copie. Un seul processus : pour plusieurs
# instances il faudrait Redis pub/sub, hors périmètre.
# Utilisé par : worker.py (publish), api.py (subscribe).
"""Bus d'événements en mémoire, un abonné = une asyncio.Queue."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

Event = dict[str, Any]


class Broadcaster:
    def __init__(self) -> None:
        self._abonnes: set[asyncio.Queue[Event]] = set()

    def publish(self, event: Event) -> None:
        for q in self._abonnes:
            q.put_nowait(event)  # jamais bloquant : la file est sans limite

    @asynccontextmanager
    async def subscribe(self) -> AsyncIterator[asyncio.Queue[Event]]:
        """`async with bus.subscribe() as q:` : abonné à l'entrée, désabonné à la sortie,
        même si le client SSE coupe la connexion (chapitre 11, les context managers)."""
        q: asyncio.Queue[Event] = asyncio.Queue()
        self._abonnes.add(q)
        try:
            yield q
        finally:
            self._abonnes.discard(q)

    @property
    def nb_abonnes(self) -> int:
        return len(self._abonnes)


bus = Broadcaster()  # l'instance unique de l'application
