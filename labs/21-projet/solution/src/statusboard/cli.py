# src/statusboard/cli.py — Labo 21 (solution) : la commande `statusboard`.
#
# Rôle : administration locale (ajouter, lister, voir l'état, lancer le serveur).
# Elle parle directement à la base, pas à l'API : c'est l'outil de l'admin sur
# la machine, l'API est pour les clients distants (chapitre 13).
# Lancé par : l'exécutable `statusboard` généré par [project.scripts].
"""CLI typer : add, list, status, check, serve."""

import asyncio
from typing import Annotated

import typer
from sqlmodel import Session, select

from statusboard import worker
from statusboard.auth import assurer_admin
from statusboard.db import get_engine, init_db, status_of
from statusboard.models import Kind, Target

app = typer.Typer(
    help="statusboard : surveille des cibles HTTP, TCP et ping.", no_args_is_help=True
)


def _session() -> Session:
    init_db()
    return Session(get_engine())


@app.command()
def add(
    name: str,
    kind: Kind,
    address: Annotated[str, typer.Argument(help="URL, hôte:port ou hôte selon le type")],
    interval: Annotated[float, typer.Option("--interval", "-i", help="secondes")] = 30.0,
) -> None:
    """Ajoute une cible."""
    with _session() as s:
        if s.exec(select(Target).where(Target.name == name)).first():
            typer.echo(f"la cible {name!r} existe déjà", err=True)
            raise typer.Exit(1)
        s.add(Target(name=name, kind=kind, address=address, interval_s=interval))
        s.commit()
    typer.echo(f"ajouté : {name} ({kind.value} {address}, toutes les {interval:g}s)")


@app.command("list")
def lister() -> None:
    """Liste les cibles."""
    with _session() as s:
        for t in s.exec(select(Target)):
            actif = "" if t.enabled else " (désactivée)"
            typer.echo(f"{t.id:>3}  {t.name:<20} {t.kind.value:<5} {t.address}{actif}")


@app.command()
def status() -> None:
    """État courant : dernier résultat de chaque cible."""
    with _session() as s:
        for t in s.exec(select(Target)):
            e = status_of(s, t)
            symbole = "?" if e.ok is None else ("UP" if e.ok else "DOWN")
            latence = f"{e.latency_ms:.0f} ms" if e.latency_ms is not None else ""
            typer.echo(f"{symbole:<4} {t.name:<20} {latence:<8} {e.detail}")


@app.command()
def check(name: str) -> None:
    """Vérifie une cible tout de suite."""
    with _session() as s:
        t = s.exec(select(Target).where(Target.name == name)).first()
        if t is None:
            typer.echo(f"cible inconnue : {name}", err=True)
            raise typer.Exit(1)
    # asyncio.run : on entre dans le monde async le temps d'une vérification.
    c = asyncio.run(worker.verifier_et_sauver(t))
    typer.echo(f"{'UP' if c.ok else 'DOWN'} {name} {c.detail}")


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Lance l'API (et le worker) avec uvicorn."""
    import uvicorn

    with _session() as s:
        assurer_admin(s)
    uvicorn.run("statusboard.api:app", host=host, port=port)


if __name__ == "__main__":
    app()
