# src/outils/cli.py — Labo 20 (solution) : la commande `outils`.
#
# Rôle : point d'entrée en ligne de commande, déclaré dans [project.scripts].
# Appelé par : l'exécutable `outils` généré par pip, ou `python -m outils.cli`.
"""Ligne de commande : outils ip|jours|port."""

import argparse
import sys
from collections.abc import Sequence
from datetime import date

from outils import dates, reseau


def main(argv: Sequence[str] | None = None) -> int:
    # argv=None → argparse lit sys.argv[1:] ; passer une liste rend main()
    # testable sans toucher à sys.argv (chapitre 13).
    p = argparse.ArgumentParser(
        prog="outils", description="Petits outils dates et réseau"
    )
    sp = p.add_subparsers(dest="cmd", required=True)

    cmd_ip = sp.add_parser("ip", help="infos sur une adresse IP")
    cmd_ip.add_argument("adresse")

    cmd_jours = sp.add_parser("jours", help="jours ouvrés entre deux dates AAAA-MM-JJ")
    cmd_jours.add_argument("debut")
    cmd_jours.add_argument("fin")

    cmd_port = sp.add_parser("port", help="teste si un port TCP répond")
    cmd_port.add_argument("hote")
    cmd_port.add_argument("port", type=int)

    args = p.parse_args(argv)

    if args.cmd == "ip":
        if not reseau.est_ip_valide(args.adresse):
            print(f"adresse invalide : {args.adresse}", file=sys.stderr)
            return 1
        genre = "privée" if reseau.est_privee(args.adresse) else "publique"
        print(f"{args.adresse} : {genre}")
    elif args.cmd == "jours":
        ouvres = dates.jours_ouvres(
            date.fromisoformat(args.debut), date.fromisoformat(args.fin)
        )
        print(len(ouvres), "jours ouvrés")
    elif args.cmd == "port":
        print("ouvert" if reseau.port_ouvert(args.hote, args.port) else "fermé")
    return 0


if __name__ == "__main__":
    sys.exit(main())
