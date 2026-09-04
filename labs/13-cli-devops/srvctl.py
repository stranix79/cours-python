#!/usr/bin/env python3
# srvctl.py — Labo 13 : un outil en ligne de commande pour gérer un inventaire de serveurs.
# Lancé par : python3 srvctl.py <commande> [options]
# Importé par : test_srvctl.py
#
# Structure (chapitre 13.9) :
#   1. fonctions pures (charger_inventaire, filtrer, trouver, masquer) → testées directement
#   2. fonctions à effets (ping_hote, lancer)                          → mockées dans les tests
#   3. les commandes typer, qui collent tout et gèrent l'affichage

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="srvctl — gère un inventaire de serveurs.", no_args_is_help=True)
console = Console()                 # stdout
erreur = Console(stderr=True)       # stderr : messages, dry-run, erreurs

INVENTAIRE_DEFAUT = Path(__file__).resolve().parent / "inventaire.json"
MOTS_SENSIBLES = ("SECRET", "TOKEN", "PASSWORD", "PASSWD", "KEY")


@dataclass
class Options:
    inventaire: Path
    json_: bool
    dry_run: bool


@app.callback()
def options_globales(
    ctx: typer.Context,
    inventaire: Annotated[Path, typer.Option("--inventaire", "-i", help="fichier JSON d'inventaire")] = INVENTAIRE_DEFAUT,
    json_: Annotated[bool, typer.Option("--json", help="sortie JSON sur stdout (pour les pipes)")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="affiche ce qui serait fait, ne le fait pas")] = False,
):
    """Options globales, lues AVANT la sous-commande : srvctl --json list."""
    ctx.obj = Options(inventaire=inventaire, json_=json_, dry_run=dry_run)


# ---------------------------------------------------------------------------
# 1. Fonctions pures
# ---------------------------------------------------------------------------
def charger_inventaire(chemin: Path) -> list[dict]:
    """Lit le JSON et rend la liste sous la clé « serveurs ».
    FileNotFoundError si le fichier manque (open s'en charge), ValueError si la clé manque."""
    # TODO : open + json.load ; vérifier que donnees["serveurs"] existe et est une liste
    raise NotImplementedError("TODO")


def filtrer(serveurs: list[dict], groupe: str | None = None, tag: str | None = None) -> list[dict]:
    """Ne garde que les serveurs du groupe et/ou portant le tag (None = pas de filtre)."""
    # TODO : une compréhension de liste avec deux conditions
    raise NotImplementedError("TODO")


def trouver(serveurs: list[dict], nom_ou_hote: str) -> str:
    """Nom d'inventaire → hôte ; si le nom est inconnu, c'est déjà un hôte : le rendre tel quel."""
    # TODO
    raise NotImplementedError("TODO")


def masquer(env: dict[str, str], prefixe: str = "") -> dict[str, str]:
    """Filtre par préfixe, trie par nom, remplace par « *** » les valeurs dont le nom
    contient un des MOTS_SENSIBLES (insensible à la casse)."""
    # TODO : sorted(env.items()), str.startswith, any(mot in cle.upper() for mot in MOTS_SENSIBLES)
    raise NotImplementedError("TODO")


# ---------------------------------------------------------------------------
# 2. Fonctions à effets
# ---------------------------------------------------------------------------
def ping_hote(hote: str, timeout: float) -> dict:
    """Un ping (subprocess.run(["ping", "-c", "1", hote], ...)) → {"hote", "ok", "detail"}.
    Attrape subprocess.TimeoutExpired (ok=False, detail contient « timeout »)
    et FileNotFoundError (ping absent). N'affiche rien, ne lève rien."""
    # TODO : capture_output=True, text=True, timeout=timeout ; ok = returncode == 0 ;
    #        detail = dernière ligne de stdout si ok, sinon de stderr
    raise NotImplementedError("TODO")


def lancer(commande: list[str], timeout: float) -> subprocess.CompletedProcess:
    """Lance une commande locale et rend le CompletedProcess."""
    # TODO : subprocess.run(commande, capture_output=True, text=True, timeout=timeout)
    raise NotImplementedError("TODO")


# ---------------------------------------------------------------------------
# 3. Commandes
# ---------------------------------------------------------------------------
def _inventaire_ou_sortie(opts: Options) -> list[dict]:
    """Charge l'inventaire ; si impossible, message sur stderr et typer.Exit(code=1)."""
    try:
        return charger_inventaire(opts.inventaire)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        erreur.print(f"[red]inventaire illisible :[/red] {e}")
        raise typer.Exit(code=1)


@app.command("list")
def lister(
    ctx: typer.Context,
    groupe: Annotated[str | None, typer.Option("--groupe", "-g")] = None,
    tag: Annotated[str | None, typer.Option("--tag", "-t")] = None,
):
    """Liste les serveurs de l'inventaire."""
    opts: Options = ctx.obj
    serveurs = filtrer(_inventaire_ou_sortie(opts), groupe, tag)
    if opts.json_:
        print(json.dumps(serveurs, ensure_ascii=False, indent=2))   # print, pas console : JSON brut
        return
    table = Table(title=f"{len(serveurs)} serveur(s)")
    for colonne in ("nom", "hôte", "groupe", "os", "tags"):
        table.add_column(colonne)
    for s in serveurs:
        table.add_row(s["nom"], s["hote"], s["groupe"], s.get("os", "?"), ", ".join(s.get("tags", [])))
    console.print(table)


@app.command()
def ping(
    ctx: typer.Context,
    cibles: Annotated[list[str] | None, typer.Argument(help="noms d'inventaire ou hôtes")] = None,
    timeout: Annotated[float, typer.Option(help="secondes par hôte")] = 2.0,
    tous: Annotated[bool, typer.Option("--all", help="tout l'inventaire")] = False,
):
    """Teste la joignabilité. Code de sortie 1 si un ping échoue, 2 si aucune cible."""
    opts: Options = ctx.obj
    serveurs = _inventaire_ou_sortie(opts)
    # TODO : hotes = tout l'inventaire si --all, sinon trouver() sur chaque cible,
    #        sinon message sur stderr + typer.Exit(code=2)
    # TODO : si opts.dry_run → afficher « dry-run : ping -c 1 <hote> » sur stderr pour chacun, et return
    # TODO : resultats = [ping_hote(h, timeout) ...] ; --json → json.dumps ; sinon une ligne
    #        OK/KO (console.print avec [green]/[red]) ; typer.Exit(code=1) si un KO
    raise NotImplementedError("TODO")


@app.command("exec")
def executer(
    ctx: typer.Context,
    commande: Annotated[list[str], typer.Argument(help="la commande et ses arguments")],
    timeout: Annotated[float, typer.Option(help="secondes")] = 30.0,
):
    """Lance une commande locale, montre stdout/stderr, et sort avec SON code de sortie.
    Exemple : srvctl exec -- ls -la /tmp"""
    opts: Options = ctx.obj
    # TODO : dry-run → afficher et return ; lancer() dans un try :
    #        FileNotFoundError → code 127, TimeoutExpired → code 124 ;
    #        --json → dict {commande, code, stdout, stderr} ; sinon stdout sur console,
    #        stderr en rouge sur erreur, « code de sortie : N » en dim ;
    #        raise typer.Exit(code=r.returncode)
    raise NotImplementedError("TODO")


@app.command()
def env(
    ctx: typer.Context,
    prefixe: Annotated[str, typer.Option("--prefixe", "-p")] = "",
):
    """Affiche les variables d'environnement, valeurs sensibles masquées."""
    opts: Options = ctx.obj
    variables = masquer(dict(os.environ), prefixe)
    # TODO : --json → json.dumps ; sinon une Table nom / valeur
    raise NotImplementedError("TODO")


if __name__ == "__main__":
    app()
