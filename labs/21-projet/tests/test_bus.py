# tests/test_bus.py — Labo 21 : le bus d'événements, seul.
import pytest

from statusboard.bus import Broadcaster


@pytest.mark.asyncio
async def test_chaque_abonne_recoit_une_copie_puis_se_desabonne() -> None:
    bus = Broadcaster()
    async with bus.subscribe() as a, bus.subscribe() as b:
        bus.publish({"n": 1})
        assert await a.get() == {"n": 1}
        assert await b.get() == {"n": 1}
        assert bus.nb_abonnes == 2
    assert bus.nb_abonnes == 0
    bus.publish({"n": 2})  # plus personne : ne doit pas planter
