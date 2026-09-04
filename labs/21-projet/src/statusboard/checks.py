# src/statusboard/checks.py — Labo 21 : les trois vérifications, en async (jalon 2).
"""Vérifications HTTP, TCP et ping. Chaque coroutine renvoie un Check non sauvegardé."""

from statusboard.models import Check, Target

TIMEOUT_S = 5.0


async def check_http(url: str) -> Check:
    # TODO : httpx.AsyncClient(timeout=TIMEOUT_S, follow_redirects=True), GET, ok si < 400,
    #        latence avec time.perf_counter(), httpx.HTTPError → Check en échec avec le nom de l'erreur.
    raise NotImplementedError("TODO jalon 2")


async def check_tcp(hote: str, port: int) -> Check:
    # TODO : asyncio.wait_for(asyncio.open_connection(hote, port), TIMEOUT_S) ; fermer le writer ;
    #        OSError / TimeoutError → échec.
    raise NotImplementedError("TODO jalon 2")


async def check_ping(hote: str) -> Check:
    # TODO : asyncio.create_subprocess_exec("ping", "-c", "1", hote, stdout/stderr DEVNULL),
    #        wait_for(proc.wait(), TIMEOUT_S) ; ok si code de retour 0 ; FileNotFoundError si pas de ping.
    raise NotImplementedError("TODO jalon 2")


async def run_check(target: Target) -> Check:
    """Aiguille selon target.kind (match), renseigne check.target_id."""
    raise NotImplementedError("TODO jalon 2")
