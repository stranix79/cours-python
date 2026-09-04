# outils.py — Labo 05 : une boîte à outils de fonctions DevOps.
# Chaque fonction est indépendante : complète-les dans l'ordre du README.

import time

UNITES = ("o", "Ko", "Mo", "Go", "To")


def taille_lisible(octets: int, decimales: int = 1) -> str:
    """Convertit un nombre d'octets en texte lisible : 1536 → '1.5 Ko'."""
    # TODO : boucle sur UNITES ; tant que octets >= 1024, divise par 1024
    #        et passe à l'unité suivante. Formatage : f"{valeur:.{decimales}f} {unite}"
    #        Cas particulier : en dessous de 1024, pas de décimale ("512 o").
    raise NotImplementedError("TODO")


def parse_kv(texte: str, sep: str = " ") -> dict[str, str | int]:
    """Transforme 'host=web01 port=22' en {'host': 'web01', 'port': 22}."""
    # TODO : texte.split(sep), puis pour chaque morceau contenant "=",
    #        str.partition("=") ou str.split("=", 1). Ignore les morceaux sans "=".
    #        Bonus : si valeur.isdigit(), convertis en int.
    raise NotImplementedError("TODO")


def slugify(texte: str) -> str:
    """'Serveur Web #1 (prod)' → 'serveur-web-1-prod'."""
    # TODO : parcours les caractères de texte.lower() ; garde ceux qui sont
    #        alphanumériques (c.isalnum()), remplace les autres par "-".
    #        Puis supprime les tirets doubles et ceux des extrémités (str.strip("-")).
    raise NotImplementedError("TODO")


def retry(fonction, essais: int = 3, attente: float = 0.0):
    """Appelle fonction() jusqu'à réussite, au plus `essais` fois.

    Renvoie le résultat de fonction() ; relance la dernière exception si
    toutes les tentatives échouent.
    """
    # TODO : boucle for sur range(essais) ; try: return fonction()
    #        except Exception as e: mémorise e, time.sleep(attente).
    #        Après la boucle : raise de l'exception mémorisée.
    #        (Le try/except est détaillé au chapitre 8 ; ici le squelette suffit :
    #         try:
    #             return fonction()
    #         except Exception as e:
    #             derniere = e )
    raise NotImplementedError("TODO")


# --- Une fonction volontairement capricieuse, pour tester retry -------------
_appels = 0


def instable() -> str:
    """Échoue deux fois, puis réussit. Simule un service qui redémarre."""
    global _appels                 # un des rares cas où global se justifie : une démo
    _appels += 1
    if _appels < 3:
        print(f"instable : échec {_appels}")
        raise ConnectionError("pas encore prêt")
    print("instable : ok")
    return "connecté"


if __name__ == "__main__":
    # Démo : ne s'exécute que si on lance `python3 outils.py`, pas à l'import.
    print(f"1536 octets      → {taille_lisible(1536)}")
    print(f"10485760 octets  → {taille_lisible(10 * 1024 * 1024)}")
    print(parse_kv("host=web01 port=22 user=root"))
    print(slugify("Serveur Web #1 (prod)"))
    retry(instable, essais=5)
