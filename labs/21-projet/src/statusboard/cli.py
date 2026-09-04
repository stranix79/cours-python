# src/statusboard/cli.py — Labo 21 : la commande `statusboard` (jalon 5).
"""CLI typer : add, list, status, check, serve."""

import typer

app = typer.Typer(help="statusboard : surveille des cibles HTTP, TCP et ping.", no_args_is_help=True)


@app.command()
def add(name: str, kind: str, address: str, interval: float = 30.0) -> None:
    """Ajoute une cible (TODO : Kind au lieu de str, --interval/-i, refus des doublons)."""
    raise NotImplementedError("TODO jalon 5")


@app.command("list")
def lister() -> None:
    raise NotImplementedError("TODO jalon 5")


@app.command()
def status() -> None:
    raise NotImplementedError("TODO jalon 5")


@app.command()
def check(name: str) -> None:
    """Vérifie une cible tout de suite (asyncio.run(worker.verifier_et_sauver(t)))."""
    raise NotImplementedError("TODO jalon 5")


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    import uvicorn

    uvicorn.run("statusboard.api:app", host=host, port=port)


if __name__ == "__main__":
    app()
