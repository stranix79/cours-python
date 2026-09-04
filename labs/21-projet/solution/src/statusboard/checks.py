# src/statusboard/checks.py — Labo 21 (solution) : les trois vérifications, en async.
#
# Rôle : une coroutine par type de cible, qui renvoie un Check non sauvegardé.
# Tout est async pour que le worker vérifie 50 cibles en parallèle sans thread
# (chapitre 15) : httpx.AsyncClient pour HTTP, asyncio.open_connection pour TCP,
# un sous-processus asyncio pour ping.
# Utilisé par : worker.py, api.py (vérification à la demande), tests.
"""Vérifications HTTP, TCP et ping."""

import asyncio
import time

import httpx

from statusboard.models import Check, Kind, Target

TIMEOUT_S = 5.0


async def check_http(url: str) -> Check:
    debut = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_S, follow_redirects=True) as client:
            r = await client.get(url)
        ms = (time.perf_counter() - debut) * 1000
        return Check(
            target_id=0, ok=r.status_code < 400, latency_ms=ms, detail=f"HTTP {r.status_code}"
        )
    except httpx.HTTPError as e:
        # Toutes les erreurs de transport d'httpx (timeout, connexion refusée, DNS…)
        # héritent de HTTPError : on en fait un check en échec, pas une exception.
        return Check(target_id=0, ok=False, detail=type(e).__name__)


async def check_tcp(hote: str, port: int) -> Check:
    debut = time.perf_counter()
    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection(hote, port), TIMEOUT_S)
    except (OSError, TimeoutError) as e:
        return Check(target_id=0, ok=False, detail=type(e).__name__)
    writer.close()
    await writer.wait_closed()
    return Check(
        target_id=0, ok=True, latency_ms=(time.perf_counter() - debut) * 1000, detail="connexion OK"
    )


async def check_ping(hote: str) -> Check:
    # ICMP brut demande root : on délègue à la commande ping du système, qui a
    # les droits qu'il faut. -c 1 : un seul paquet. Le délai est géré par wait_for.
    debut = time.perf_counter()
    try:
        proc = await asyncio.create_subprocess_exec(
            "ping",
            "-c",
            "1",
            hote,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        code = await asyncio.wait_for(proc.wait(), TIMEOUT_S)
    except TimeoutError:
        proc.kill()
        return Check(target_id=0, ok=False, detail="timeout")
    except FileNotFoundError:
        return Check(target_id=0, ok=False, detail="commande ping absente")
    ms = (time.perf_counter() - debut) * 1000
    return Check(
        target_id=0, ok=code == 0, latency_ms=ms if code == 0 else None, detail=f"ping code {code}"
    )


async def run_check(target: Target) -> Check:
    """Aiguille vers la bonne vérification et renseigne target_id."""
    match target.kind:
        case Kind.http:
            check = await check_http(target.address)
        case Kind.tcp:
            hote, _, port = target.address.rpartition(":")
            check = await check_tcp(hote, int(port))
        case Kind.ping:
            check = await check_ping(target.address)
    assert target.id is not None, "la cible doit être en base avant d'être vérifiée"
    check.target_id = target.id
    return check
