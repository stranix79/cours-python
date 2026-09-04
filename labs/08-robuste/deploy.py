# deploy.py — Labo 08 : simuler un déploiement à partir d'un config.json et d'un fichier de hosts.
#
# Usage : python3 deploy.py data/config.json data/hosts.txt
#
# Version naïve : tout marche quand les fichiers sont parfaits, et plante
# avec un traceback brut dès qu'un fichier manque, est mal formé ou incomplet.
# Ton travail : la rendre robuste sans la rendre bavarde.

import json
import sys

# TODO : import logging, et configurer deux handlers :
#   - console (stderr) au niveau INFO, format court « INFO: message »
#   - fichier deploy.log au niveau DEBUG, format long avec date, niveau, nom, message
#   Voir chapitre 8, section 8.8 (« Console et fichier à deux niveaux différents »).

# TODO : définir une exception ConfigError(Exception) pour tout ce qui concerne
#   le fichier de configuration (absent, illisible, JSON cassé, clé manquante,
#   valeur du mauvais type).

CLES_OBLIGATOIRES = ("service", "port", "image", "replicas")


def charger_config(chemin):
    # TODO : attraper FileNotFoundError, PermissionError, json.JSONDecodeError
    #   et relever une ConfigError avec un message clair, chaînée (raise ... from e).
    # TODO : vérifier que chaque clé de CLES_OBLIGATOIRES est présente (KeyError → ConfigError).
    # TODO : vérifier que port et replicas sont des int (TypeError/ValueError → ConfigError).
    with open(chemin, encoding="utf-8") as f:
        config = json.load(f)
    return config


def charger_hosts(chemin):
    # TODO : ignorer les lignes vides et celles qui commencent par « # ».
    # TODO : si la liste est vide à la fin, lever ValueError("aucun hôte").
    # TODO : fichier absent / illisible : laisser remonter OSError ? ou convertir ?
    #   Décide, et documente ton choix dans un commentaire.
    with open(chemin, encoding="utf-8") as f:
        return [ligne.strip() for ligne in f]


def deployer(config, hosts):
    # Simulation : on affiche ce qu'on ferait. Rien à changer ici.
    for hote in hosts:
        print(f"[{hote}] docker run -d -p {config['port']}:{config['port']} "
              f"--name {config['service']} {config['image']}  (x{config['replicas']})")


def main(argv):
    # TODO : vérifier qu'il y a bien deux arguments, sinon afficher l'usage et sortir avec le code 64.
    # TODO : envelopper le tout :
    #   ConfigError      → log.error(message), code de sortie 2
    #   erreur de hosts  → log.error(message), code de sortie 3
    #   KeyboardInterrupt → log.warning("interrompu"), code 130
    #   toute autre Exception → log.exception("erreur inattendue"), code 1
    #   succès            → log.info("déploiement simulé sur N hôtes"), code 0
    config = charger_config(argv[1])
    hosts = charger_hosts(argv[2])
    deployer(config, hosts)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
