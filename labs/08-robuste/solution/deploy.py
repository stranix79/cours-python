# solution/deploy.py — Labo 08 : simuler un déploiement, version robuste et commentée.
#
# Rôle : lire un config.json et un fichier de hosts, afficher les commandes
#        qu'on lancerait, et surtout : échouer PROPREMENT quand une entrée est
#        mauvaise, avec un message utile et un code de sortie exploitable par le shell.
# Lancé par : python3 solution/deploy.py data/config.json data/hosts.txt
#
# Codes de sortie (convention Unix : 0 = succès, le reste = échec, chaque valeur
# a un sens pour celui qui appelle le script depuis un shell ou un pipeline) :
#   0   succès
#   1   erreur inattendue (bug) : le traceback est dans deploy.log
#   2   fichier de configuration inutilisable
#   3   fichier de hosts inutilisable
#   64  usage incorrect (EX_USAGE de sysexits.h, l'habitude vient de BSD)
#   130 interrompu par Ctrl-C (128 + SIGINT, comme le fait le shell lui-même)

import json
import logging
import sys

# ---------------------------------------------------------------------------
# Logging : deux destinations, deux niveaux.
# Le logger racine laisse tout passer (DEBUG) ; ce sont les handlers qui trient.
# ---------------------------------------------------------------------------
racine = logging.getLogger()
racine.setLevel(logging.DEBUG)

# La console (stderr) ne montre que l'essentiel : l'utilisateur n'a pas besoin
# de savoir quelle fonction a lu quel fichier. stderr et non stdout, pour que
# la sortie « utile » (les commandes docker) reste pipable : deploy.py ... | grep web-01
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

# Le fichier garde tout, avec la date et l'endroit exact dans le code :
# c'est lui qu'on ouvre quand ça a raté à 3 h du matin dans un cron.
fichier = logging.FileHandler("deploy.log", encoding="utf-8")
fichier.setLevel(logging.DEBUG)
fichier.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)-8s %(name)s %(funcName)s:%(lineno)d %(message)s"))

racine.addHandler(console)
racine.addHandler(fichier)

# Le logger de CE module. Dans un script lancé directement, __name__ vaut
# "__main__" ; si un jour deploy.py est importé par un autre script, les
# messages seront étiquetés "deploy" et resteront attribuables.
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions maison.
# Une classe vide qui hérite d'Exception suffit : ce qui compte, c'est le TYPE,
# qui permet à main() d'écrire « except ConfigError » sans attraper les
# ValueError de tout le programme.
# ---------------------------------------------------------------------------
class ConfigError(Exception):
    """Le fichier de configuration est absent, illisible, mal formé ou incomplet."""


class HostsError(Exception):
    """Le fichier de hosts est absent, illisible ou vide."""


CLES_OBLIGATOIRES = ("service", "port", "image", "replicas")


def charger_config(chemin: str) -> dict:
    """Lit et valide le JSON de configuration. Lève ConfigError sinon."""
    log.debug("lecture de la configuration %s", chemin)
    # Remarque : log.debug("... %s", chemin) et non f"...{chemin}" : logging ne
    # construit la chaîne que si le message passe le filtre de niveau. Avec une
    # f-string, on paierait le formatage même quand le message est jeté.

    # Un seul try pour les trois erreurs « système », chacune convertie en
    # ConfigError avec un message écrit pour un humain. Le « from e » conserve
    # la cause : dans deploy.log on retrouvera le errno ou la position du JSON cassé.
    try:
        with open(chemin, encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError as e:
        raise ConfigError(f"configuration introuvable : {chemin}") from e
    except PermissionError as e:
        raise ConfigError(f"configuration illisible (permissions) : {chemin}") from e
    except json.JSONDecodeError as e:
        # e.lineno / e.colno : la position exacte de l'erreur de syntaxe.
        raise ConfigError(
            f"JSON invalide dans {chemin}, ligne {e.lineno} colonne {e.colno} : {e.msg}"
        ) from e

    # EAFP : on ne teste pas « if cle in config » avant d'y accéder, on accède
    # et on attrape KeyError. Ici on veut un message qui liste TOUTES les clés
    # manquantes d'un coup, donc une compréhension + un seul raise.
    manquantes = [cle for cle in CLES_OBLIGATOIRES if cle not in config]
    if manquantes:
        raise ConfigError(f"clé(s) manquante(s) dans {chemin} : {', '.join(manquantes)}")

    # Validation des types. json.load donne des int pour 8443 et des str pour
    # "huit mille" : on refuse ce qui n'est pas un entier. isinstance et non
    # int(...) : int("8443") marcherait mais masquerait une config mal typée.
    for cle in ("port", "replicas"):
        if not isinstance(config[cle], int):
            raise ConfigError(
                f"{cle} doit être un entier, reçu {config[cle]!r} ({type(config[cle]).__name__})"
            )

    log.debug("configuration valide : %s", config)
    return config


def charger_hosts(chemin: str) -> list[str]:
    """Lit la liste des hôtes (un par ligne, # = commentaire). Lève HostsError sinon."""
    log.debug("lecture des hôtes %s", chemin)

    # Choix : on convertit aussi les OSError en HostsError, pour que main() n'ait
    # à connaître que deux exceptions « métier » et deux codes de sortie.
    # OSError est le parent de FileNotFoundError et PermissionError : un seul
    # except suffit, et e.strerror donne le texte système (« No such file... »).
    try:
        with open(chemin, encoding="utf-8") as f:
            lignes = [ligne.strip() for ligne in f]
    except OSError as e:
        raise HostsError(f"fichier de hosts illisible : {chemin} ({e.strerror})") from e

    hosts = [l for l in lignes if l and not l.startswith("#")]
    log.debug("%d ligne(s) lue(s), %d hôte(s) retenu(s)", len(lignes), len(hosts))

    if not hosts:
        raise HostsError(f"aucun hôte dans {chemin}")
    return hosts


def deployer(config: dict, hosts: list[str]) -> None:
    """Simulation : affiche sur stdout ce qu'on lancerait."""
    for hote in hosts:
        log.debug("déploiement sur %s", hote)
        print(f"[{hote}] docker run -d -p {config['port']}:{config['port']} "
              f"--name {config['service']} {config['image']}  (x{config['replicas']})")


def main(argv: list[str]) -> int:
    """Point d'entrée. Renvoie le code de sortie, c'est sys.exit qui le transmet au shell."""
    if len(argv) != 3:
        print(f"usage : {argv[0]} config.json hosts.txt", file=sys.stderr)
        return 64

    # Un seul try autour de tout le travail. Chaque except correspond à UNE
    # catégorie d'échec et UN code de sortie. L'ordre compte : du plus précis
    # au plus général, Exception en dernier.
    try:
        config = charger_config(argv[1])
        hosts = charger_hosts(argv[2])
        deployer(config, hosts)
    except ConfigError as e:
        # log.error suffit : le message a été écrit pour un humain, et la cause
        # technique est déjà dans le chaînage. Pour la voir, on l'ajoute au
        # fichier seulement, avec exc_info=True, sans polluer la console.
        log.error("%s", e)
        log.debug("détail", exc_info=True)
        return 2
    except HostsError as e:
        log.error("%s", e)
        log.debug("détail", exc_info=True)
        return 3
    except KeyboardInterrupt:
        # Hérite de BaseException, pas d'Exception : le « except Exception »
        # ci-dessous ne l'attraperait PAS. On le traite explicitement pour
        # sortir proprement avec le code que le shell attend.
        log.warning("interrompu par l'utilisateur")
        return 130
    except Exception:
        # Tout le reste est un BUG (pas une erreur d'entrée). log.exception
        # écrit le traceback complet : c'est la seule chose qui permettra de
        # le corriger. Ici, et seulement ici, on attrape large.
        log.exception("erreur inattendue")
        return 1

    log.info("déploiement simulé sur %d hôte(s)", len(hosts))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
