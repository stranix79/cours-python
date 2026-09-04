# src/statusboard/bus.py — Labo 21 : diffusion d'événements aux clients SSE (jalon 3).
"""Bus d'événements en mémoire : un abonné = une asyncio.Queue."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

Event = dict[str, Any]


class Broadcaster:
    def __init__(self) -> None:
        self._abonnes: set[asyncio.Queue[Event]] = set()

    def publish(self, event: Event) -> None:
        # TODO : put_nowait dans chaque file abonnée.
        raise NotImplementedError("TODO jalon 3")

    @asynccontextmanager
    async def subscribe(self) -> AsyncIterator[asyncio.Queue[Event]]:
        # TODO : créer une Queue, l'ajouter, yield, la retirer dans un finally.
        raise NotImplementedError("TODO jalon 3")
        yield  # pour que la fonction reste un générateur async

    @property
    def nb_abonnes(self) -> int:
        return len(self._abonnes)


bus = Broadcaster()
