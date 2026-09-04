# solution/inventaire.py — Labo 07 : inventaire de machines, version commentée.
#
# Rôle : gérer une liste de serveurs dans data/inventaire.json, l'exporter et
# l'importer en CSV. Lancé par : python3 solution/inventaire.py <commande> ...
#
# Structure classique d'un script d'administration :
#   charger() → modifier la liste en mémoire → sauver()
# Le fichier n'est jamais modifié « en place » : on relit tout, on réécrit tout.
# Pour quelques centaines de machines c'est instantané ; au-delà on passerait
# à SQLite (chapitre 18).

import csv
import json
import sys
from collections import Counter
from pathlib import Path

# __file__ est le chemin de CE fichier. Son parent est le dossier du script :
# les données sont donc toujours à côté du script, d'où qu'on le lance.
DOSSIER = Path(__file__).parent / "data"
FICHIER = DOSSIER / "inventaire.json"
COLONNES = ["nom", "ip", "role", "ports"]        # l'ordre des colonnes CSV

USAGE = """usage : inventaire.py <commande> [arguments]

  ajouter   <nom> <ip> <role> [port ...]
  lister
  chercher  <texte>
  supprimer <nom>
  exporter  <fichier.csv>
  importer  <fichier.csv>
  stats
"""


# ---------------------------------------------------------------- persistance

def charger() -> list[dict]:
    """Lit data/inventaire.json ; liste vide si le fichier n'existe pas."""
    if not FICHIER.exists():
        return []
    # open() accepte un Path. encoding explicite, toujours (chapitre 7.1).
    with open(FICHIER, encoding="utf-8") as f:
        return json.load(f)             # le JSON [...] devient une list de dict


def sauver(machines: list[dict]) -> None:
    """Écrit la liste dans data/inventaire.json, de façon atomique.

    On écrit d'abord dans un fichier temporaire à côté, puis on le renomme
    par-dessus le vrai. rename() est atomique sur un même système de
    fichiers : à tout instant, inventaire.json est soit l'ancienne version
    complète, soit la nouvelle complète, jamais un fichier à moitié écrit.
    C'est ce que font les éditeurs, apt, et tous les outils sérieux.
    """
    DOSSIER.mkdir(parents=True, exist_ok=True)      # mkdir -p, silencieux si existe
    temporaire = FICHIER.with_suffix(".json.tmp")   # inventaire.json.tmp
    with open(temporaire, "w", encoding="utf-8") as f:
        # indent=2 : lisible dans un éditeur et diffable dans git.
        # ensure_ascii=False : « Liège » reste « Liège » dans le fichier.
        json.dump(machines, f, indent=2, ensure_ascii=False)
        f.write("\n")                               # fin de fichier propre, comme un éditeur
    temporaire.replace(FICHIER)                     # mv atomique, écrase l'ancien


def trouver(machines: list[dict], nom: str) -> dict | None:
    """La machine qui porte ce nom, ou None."""
    # Retour anticipé dès qu'on trouve ; None implicite... rendu explicite ici.
    for m in machines:
        if m["nom"] == nom:
            return m
    return None


def afficher(m: dict) -> None:
    """Une ligne alignée. :<10 = aligné à gauche sur 10 caractères."""
    ports = ", ".join(map(str, m["ports"]))         # [22, 80] → "22, 80"
    print(f"{m['nom']:<10} {m['ip']:<16} {m['role']:<10} {ports}")


# ------------------------------------------------------------------ commandes
# Chaque commande reçoit les arguments restants (sans son propre nom), fait
# son travail, et affiche. Même signature partout → table de dispatch.

def cmd_ajouter(args: list[str]) -> None:
    nom, ip, role = args[0], args[1], args[2]       # IndexError si manquant : géré dans main()
    ports = [int(p) for p in args[3:]]              # ValueError si "abc" : idem
    machines = charger()
    if trouver(machines, nom) is not None:
        print(f"{nom} existe déjà", file=sys.stderr)
        sys.exit(1)
    machines.append({"nom": nom, "ip": ip, "role": role, "ports": ports})
    sauver(machines)
    print(f"{nom} ajouté")


def cmd_lister(args: list[str]) -> None:
    print(f"{'nom':<10} {'ip':<16} {'rôle':<10} ports")
    for m in charger():
        afficher(m)


def cmd_chercher(args: list[str]) -> None:
    texte = args[0].lower()
    for m in charger():
        # any() est vrai dès qu'un élément du générateur est vrai : on teste
        # les trois champs sans écrire trois `or`.
        if any(texte in str(m[champ]).lower() for champ in ("nom", "ip", "role")):
            afficher(m)


def cmd_supprimer(args: list[str]) -> None:
    nom = args[0]
    machines = charger()
    # Compréhension : on reconstruit la liste SANS la machine visée. Plus
    # simple et plus sûr que de supprimer pendant qu'on itère (chapitre 4).
    restantes = [m for m in machines if m["nom"] != nom]
    if len(restantes) == len(machines):
        print(f"{nom} introuvable", file=sys.stderr)
        sys.exit(1)
    sauver(restantes)
    print(f"{nom} supprimé")


def cmd_exporter(args: list[str]) -> None:
    destination = Path(args[0])
    machines = charger()
    # newline="" est exigé par le module csv : c'est lui qui gère les fins de
    # ligne, pas la couche texte de open().
    with open(destination, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES)
        w.writeheader()
        for m in machines:
            # CSV ne connaît pas les listes : on aplatit les ports en "22;80;443".
            # On copie le dict (m | {...}) plutôt que de modifier m : la liste
            # en mémoire reste intacte (chapitre 10, références).
            w.writerow(m | {"ports": ";".join(map(str, m["ports"]))})
    print(f"{len(machines)} machine(s) exportée(s) vers {destination}")


def cmd_importer(args: list[str]) -> None:
    source = Path(args[0])
    machines = charger()
    importees = presentes = 0
    with open(source, newline="", encoding="utf-8") as f:
        for ligne in csv.DictReader(f):             # une ligne = un dict, clés = en-tête
            if trouver(machines, ligne["nom"]) is not None:
                presentes += 1
                continue
            # Tout sort du CSV en chaîne : on reconstruit la liste d'entiers.
            # Le `if p` ignore une colonne ports vide ("".split(";") → [""]).
            ports = [int(p) for p in ligne["ports"].split(";") if p]
            machines.append({"nom": ligne["nom"], "ip": ligne["ip"],
                             "role": ligne["role"], "ports": ports})
            importees += 1
    sauver(machines)
    print(f"{importees} machine(s) importée(s), {presentes} déjà présente(s)")


def cmd_stats(args: list[str]) -> None:
    # Counter compte les occurrences : Counter(["web", "base", "web"]) → {"web": 2, "base": 1}
    par_role = Counter(m["role"] for m in charger())
    for role, nombre in par_role.most_common():     # trié par fréquence décroissante
        print(f"{role:<10} {nombre}")


COMMANDES = {
    "ajouter": cmd_ajouter,
    "lister": cmd_lister,
    "chercher": cmd_chercher,
    "supprimer": cmd_supprimer,
    "exporter": cmd_exporter,
    "importer": cmd_importer,
    "stats": cmd_stats,
}


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] not in COMMANDES:
        print(USAGE, file=sys.stderr)
        sys.exit(1)
    try:
        COMMANDES[args[0]](args[1:])
    except (IndexError, ValueError) as e:
        # Argument manquant (IndexError) ou port non numérique (ValueError).
        # Le vrai traitement des erreurs, avec ses propres exceptions, c'est
        # le chapitre 8. Ici on se contente d'un message et d'un code de retour.
        print(f"arguments invalides : {e}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError as e:
        print(f"fichier introuvable : {e.filename}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
