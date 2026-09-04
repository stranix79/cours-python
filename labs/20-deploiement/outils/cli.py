# outils/cli.py — Labo 20 : la commande `outils`. Volontairement sale.
import argparse, sys
from datetime import date
from outils import dates, reseau

def main(argv = None):
    p = argparse.ArgumentParser(prog="outils", description="Petits outils dates et réseau")
    sp = p.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("ip", help="infos sur une adresse IP")
    a.add_argument("adresse")
    b = sp.add_parser("jours", help="jours ouvrés entre deux dates AAAA-MM-JJ")
    b.add_argument("debut")
    b.add_argument("fin")
    c = sp.add_parser("port", help="teste si un port TCP répond")
    c.add_argument("hote")
    c.add_argument("port", type=int)
    args = p.parse_args(argv)
    if args.cmd == "ip":
        if reseau.est_ip_valide(args.adresse) == False:
            print("adresse invalide : %s" % args.adresse)
            return 1
        print("%s : %s" % (args.adresse, "privée" if reseau.est_privee(args.adresse) else "publique"))
    elif args.cmd == "jours":
        l = dates.jours_ouvres(date.fromisoformat(args.debut), date.fromisoformat(args.fin))
        print(len(l), "jours ouvrés")
    elif args.cmd == "port":
        print("ouvert" if reseau.port_ouvert(args.hote, args.port) else "fermé")
    return 0

if __name__ == "__main__":
    sys.exit(main())
