#!/usr/bin/env python3
# solution/srvctl.py — Labo 13 : un outil en ligne de commande pour gérer un inventaire de serveurs.
#
# Rôle : sous-commandes list / ping / exec / env, sortie humaine (tableaux rich)
#        ou JSON (--json, pour les pipes), et --dry-run pour ne rien lancer.
# Lancé par : python3 srvctl.py <commande> [options]   (ou ./srvctl.py après chmod +x)
# Importé par : test_srvctl.py, qui appelle les fonctions pures et invoque
#        l'application avec typer.testing.CliRunner sans jamais lancer de vrai ping.
#
# Structure (chapitre 13.9) :
#   1. fonctions pures (charger_inventaire, filtrer, masquer)   → testées directement
#   2. fonctions à effets (ping_hote, lancer)                    → mockées dans les tests
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
console = Console()                 # écrit sur sys.stdout ; rich désactive les couleurs si ce n'est pas un terminal
erreur = Console(stderr=True)       # une seconde console pour stderr : le JSON de stdout reste propre

# L'inventaire par défaut : à côté du script, sinon dans le dossier parent
# (solution/srvctl.py doit trouver labs/13-cli-devops/inventaire.json).
_ICI = Path(__file__).resolve().parent
INVENTAIRE_DEFAUT = next(
    (p for p in (_ICI / "inventaire.json", _ICI.parent / "inventaire.json") if p.exists()),
    _ICI / "inventaire.json",
)
MOTS_SENSIBLES = ("SECRET", "TOKEN", "PASSWORD", "PASSWD", "KEY")


# ---------------------------------------------------------------------------
# Options globales. typer les met dans un objet partagé par toutes les commandes.
# ---------------------------------------------------------------------------
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
    """Le callback est appelé AVANT la sous-commande : c'est là qu'on lit les options
    placées avant le nom de la commande (srvctl --json list). ctx.obj est un
    emplacement libre pour passer des données aux commandes."""
    ctx.obj = Options(inventaire=inventaire, json_=json_, dry_run=dry_run)


# ---------------------------------------------------------------------------
# 1. Fonctions pures : entrées → sortie, pas d'affichage, pas de sys.exit.
# ---------------------------------------------------------------------------
def charger_inventaire(chemin: Path) -> list[dict]:
    """Lit le JSON et rend la liste des serveurs. Lève FileNotFoundError ou ValueError."""
    with open(chemin, encoding="utf-8") as f:
        donnees = json.load(f)
    if "serveurs" not in donnees or not isinstance(donnees["serveurs"], list):
        raise ValueError(f"{chemin} : clé « serveurs » absente ou invalide")
    return donnees["serveurs"]


def filtrer(serveurs: list[dict], groupe: str | None = None, tag: str | None = None) -> list[dict]:
    """Ne garde que les serveurs du groupe et/ou portant le tag (None = pas de filtre)."""
    return [
        s for s in serveurs
        if (groupe is None or s.get("groupe") == groupe)
        and (tag is None or tag in s.get("tags", []))
    ]


def trouver(serveurs: list[dict], nom_ou_hote: str) -> str:
    """Traduit un nom d'inventaire en hôte ; si inconnu, on suppose que c'est déjà un hôte."""
    for s in serveurs:
        if s["nom"] == nom_ou_hote:
            return s["hote"]
    return nom_ou_hote


def masquer(env: dict[str, str], prefixe: str = "") -> dict[str, str]:
    """Filtre les variables par préfixe et remplace les valeurs sensibles par ***.
    Un dict en entrée, un dict en sortie : testable sans toucher à os.environ."""
    resultat = {}
    for cle, valeur in sorted(env.items()):
        if not cle.startswith(prefixe):
            continue
        if any(mot in cle.upper() for mot in MOTS_SENSIBLES):
            valeur = "***"
        resultat[cle] = valeur
    return resultat


# ---------------------------------------------------------------------------
# 2. Fonctions à effets : chacune fait UNE chose avec l'extérieur.
#    Dans les tests, monkeypatch.setattr(subprocess, "run", faux) les neutralise.
# ---------------------------------------------------------------------------
def ping_hote(hote: str, timeout: float) -> dict:
    """Un ping, un résultat : {"hote", "ok", "detail"}. N'affiche rien."""
    try:
        # Liste, jamais une chaîne : « hote » ne peut pas injecter de commande.
        # -c 1 : un seul paquet. Le timeout global est géré par Python, pas par ping
        # (l'option diffère entre macOS -t et Linux -W).
        r = subprocess.run(["ping", "-c", "1", hote], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"hote": hote, "ok": False, "detail": f"timeout après {timeout}s"}
    except FileNotFoundError:
        return {"hote": hote, "ok": False, "detail": "commande ping introuvable"}
    if r.returncode == 0:
        # La dernière ligne de ping ressemble à « round-trip min/avg/max/stddev = 0.05/... ms »
        return {"hote": hote, "ok": True, "detail": r.stdout.strip().splitlines()[-1]}
    detail = (r.stderr or r.stdout).strip().splitlines()
    return {"hote": hote, "ok": False, "detail": detail[-1] if detail else f"code {r.returncode}"}


def lancer(commande: list[str], timeout: float) -> subprocess.CompletedProcess:
    """Lance une commande locale et rend le CompletedProcess (stdout, stderr, returncode)."""
    return subprocess.run(commande, capture_output=True, text=True, timeout=timeout)


# ---------------------------------------------------------------------------
# 3. Les commandes. Elles lisent ctx.obj, appellent 1 et 2, affichent.
# ---------------------------------------------------------------------------
def _inventaire_ou_sortie(opts: Options) -> list[dict]:
    """Charge l'inventaire ; en cas d'erreur, message sur stderr et code de sortie 1."""
    try:
        return charger_inventaire(opts.inventaire)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        erreur.print(f"[red]inventaire illisible :[/red] {e}")
        raise typer.Exit(code=1)       # typer.Exit = sys.exit propre, sans traceback


@app.command("list")
def lister(
    ctx: typer.Context,
    groupe: Annotated[str | None, typer.Option("--groupe", "-g", help="ne garder qu'un groupe")] = None,
    tag: Annotated[str | None, typer.Option("--tag", "-t", help="ne garder qu'un tag")] = None,
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
    """Teste la joignabilité d'un ou plusieurs serveurs. Code de sortie 1 si un ping échoue."""
    opts: Options = ctx.obj
    serveurs = _inventaire_ou_sortie(opts)
    if tous:
        hotes = [s["hote"] for s in serveurs]
    elif cibles:
        hotes = [trouver(serveurs, c) for c in cibles]
    else:
        erreur.print("[red]donne au moins une cible, ou --all[/red]")
        raise typer.Exit(code=2)      # 2 = erreur d'usage, comme argparse

    if opts.dry_run:
        for h in hotes:
            erreur.print(f"[yellow]dry-run :[/yellow] ping -c 1 {h}")
        return

    resultats = [ping_hote(h, timeout) for h in hotes]

    if opts.json_:
        print(json.dumps(resultats, ensure_ascii=False, indent=2))
    else:
        for r in resultats:
            etat = "[green]OK  [/green]" if r["ok"] else "[red]KO  [/red]"
            console.print(f"{etat} {r['hote']:28} {r['detail']}")

    if not all(r["ok"] for r in resultats):
        raise typer.Exit(code=1)


@app.command("exec")
def executer(
    ctx: typer.Context,
    commande: Annotated[list[str], typer.Argument(help="la commande et ses arguments")],
    timeout: Annotated[float, typer.Option(help="secondes")] = 30.0,
):
    """Lance une commande locale et montre stdout, stderr et le code de sortie.
    Le code de sortie de srvctl est celui de la commande.

    Exemple : srvctl exec -- ls -la /tmp   (le -- sépare nos options des siennes)"""
    opts: Options = ctx.obj
    if opts.dry_run:
        erreur.print(f"[yellow]dry-run :[/yellow] {' '.join(commande)}")
        return
    try:
        r = lancer(commande, timeout)
    except FileNotFoundError:
        erreur.print(f"[red]commande introuvable :[/red] {commande[0]}")
        raise typer.Exit(code=127)    # 127 = « command not found » en shell
    except subprocess.TimeoutExpired:
        erreur.print(f"[red]timeout après {timeout}s[/red]")
        raise typer.Exit(code=124)    # 124 = le code de la commande timeout(1)

    if opts.json_:
        print(json.dumps({"commande": commande, "code": r.returncode,
                          "stdout": r.stdout, "stderr": r.stderr}, ensure_ascii=False, indent=2))
    else:
        if r.stdout:
            console.print(r.stdout, end="")
        if r.stderr:
            erreur.print(f"[red]{r.stderr}[/red]", end="")
        erreur.print(f"[dim]code de sortie : {r.returncode}[/dim]")
    raise typer.Exit(code=r.returncode)


@app.command()
def env(
    ctx: typer.Context,
    prefixe: Annotated[str, typer.Option("--prefixe", "-p", help="ne garder que les variables commençant par…")] = "",
):
    """Affiche les variables d'environnement, valeurs sensibles masquées."""
    opts: Options = ctx.obj
    variables = masquer(dict(os.environ), prefixe)     # dict(os.environ) : une copie ordinaire
    if opts.json_:
        print(json.dumps(variables, ensure_ascii=False, indent=2))
        return
    table = Table(title=f"{len(variables)} variable(s)")
    table.add_column("nom")
    table.add_column("valeur")
    for cle, valeur in variables.items():
        table.add_row(cle, valeur)
    console.print(table)


if __name__ == "__main__":
    app()                              # typer gère lui-même sys.exit et les codes de sortie
