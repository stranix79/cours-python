# tests/test_worker.py — Labo 21 : un tick du worker, à la main.
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from statusboard import worker
from statusboard.bus import bus
from statusboard.db import get_engine
from statusboard.models import Target


@pytest.mark.asyncio
async def test_tick_verifie_les_cibles_dues(client: TestClient, serveur_local: str) -> None:
    with Session(get_engine()) as s:
        s.add(Target(name="ok", kind="http", address=f"{serveur_local}/ok", interval_s=3600))
        s.add(Target(name="ko", kind="http", address=f"{serveur_local}/ko", interval_s=3600))
        s.add(Target(name="off", kind="http", address=f"{serveur_local}/ok", enabled=False))
        s.commit()

    recus = []
    async with bus.subscribe() as file:
        checks = await worker.tick()
        while not file.empty():
            recus.append(file.get_nowait())

    assert {c.target_id for c in checks} == {1, 2}  # "off" n'est pas vérifiée
    assert sorted(e["target"] for e in recus) == ["ko", "ok"]
    assert not any(e["changed"] for e in recus)  # première vérification : pas de changement
    assert await worker.tick() == []  # rien n'est dû avant 3600 s
