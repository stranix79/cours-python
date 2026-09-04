# solution/outils.py — Labo 05 : boîte à outils DevOps, version commentée.
#
# Rôle : quatre fonctions réutilisables (tailles, clé=valeur, slug, retry).
# Lancé par : python3 solution/outils.py (démo), ou importé par un autre
# module (import outils) : dans ce cas la démo du bas ne s'exécute pas.
# Ce module devient un paquet au labo 06.

import time

# Constante de module : par convention en MAJUSCULES. Un tuple plutôt qu'une
# liste, parce qu'on ne le modifiera jamais (immuable, chapitre 4).
UNITES = ("o", "Ko", "Mo", "Go", "To")


def taille_lisible(octets: int, decimales: int = 1) -> str:
    """Convertit un nombre d'octets en texte lisible : 1536 → '1.5 Ko'.

    Base 1024 (comme `ls -h`, `df -h`). Au-delà du To, on reste en To.
    """
    # En dessous de 1024, un entier est plus naturel que "512.0 o".
    if octets < 1024:
        return f"{octets} o"

    # On travaille sur une copie flottante : un paramètre est une variable
    # locale, la réaffecter ne change rien chez l'appelant (chapitre 10).
    valeur = float(octets)
    for unite in UNITES:
        if valeur < 1024:
            break                      # on a trouvé la bonne unité
        valeur /= 1024
    else:
        # for/else (chapitre 3) : on arrive ici si la boucle n'a PAS été
        # interrompue par break, donc valeur >= 1024 même en To. On garde To.
        unite = UNITES[-1]
        valeur *= 1024                 # on avait divisé une fois de trop

    # Le nombre de décimales est lui-même une expression dans l'f-string :
    # {valeur:.{decimales}f} → {valeur:.1f} par défaut.
    return f"{valeur:.{decimales}f} {unite}"


def parse_kv(texte: str, sep: str = " ") -> dict[str, str | int]:
    """Transforme 'host=web01 port=22' en {'host': 'web01', 'port': 22}.

    Les morceaux sans '=' sont ignorés. Les valeurs entièrement numériques
    sont converties en int.
    """
    resultat: dict[str, str | int] = {}
    for morceau in texte.split(sep):
        if "=" not in morceau:
            continue
        # partition coupe au PREMIER "=" et renvoie toujours 3 éléments :
        # "a=b=c".partition("=") → ("a", "=", "b=c"). Ainsi une valeur
        # contenant "=" (une URL avec query string) reste entière.
        cle, _, valeur = morceau.partition("=")
        # Le ternaire Python : valeur_si_vrai if condition else valeur_si_faux.
        resultat[cle.strip()] = int(valeur) if valeur.isdigit() else valeur
    return resultat


def slugify(texte: str) -> str:
    """'Serveur Web #1 (prod)' → 'serveur-web-1-prod'.

    Utile pour des noms de fichiers, d'URL, de conteneurs.
    """
    # Compréhension de liste (chapitre 4) : un caractère par élément.
    # isalnum() est vrai pour lettres et chiffres, y compris accentués ;
    # on n'enlève pas les accents ici (voir "Pour aller plus loin" : unicodedata).
    caracteres = [c if c.isalnum() else "-" for c in texte.lower()]
    slug = "".join(caracteres)          # "".join(liste) recolle les morceaux
    # Tant qu'il reste des tirets doubles, on les réduit. Une regex
    # (re.sub("-+", "-", slug), chapitre 6) ferait ça en une ligne.
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")              # strip(car) enlève car aux deux bouts


def retry(fonction, *args, essais: int = 3, attente: float = 0.0, **kwargs):
    """Appelle fonction(*args, **kwargs) jusqu'à réussite, au plus `essais` fois.

    Renvoie le résultat du premier appel qui réussit. Si toutes les
    tentatives lèvent une exception, relance la dernière.

    `fonction` est un objet fonction, passé SANS parenthèses par l'appelant :
    retry(instable), pas retry(instable()). C'est retry qui l'appelle.
    """
    # `essais` et `attente` sont après *args : ils ne peuvent être donnés que
    # par leur nom (keyword-only). Sinon retry(f, 5) serait ambigu : 5 est-il
    # un argument de f ou le nombre d'essais ?
    derniere_erreur: Exception | None = None
    for numero in range(1, essais + 1):
        try:
            return fonction(*args, **kwargs)      # succès : on sort tout de suite
        except Exception as e:                    # chapitre 8 pour les détails
            derniere_erreur = e
            if numero < essais and attente > 0:
                time.sleep(attente)
    # On ne passe ici que si aucun return n'a eu lieu : tout a échoué.
    # `raise` seul relancerait l'exception courante, mais on est hors du
    # except ; on relance donc explicitement l'objet mémorisé.
    assert derniere_erreur is not None
    raise derniere_erreur


# --- Une fonction volontairement capricieuse, pour tester retry -------------
# Le préfixe _ signale « privé au module » : c'est une convention, pas une
# protection (Python n'a pas de private). Voir chapitre 9.
_appels = 0


def instable() -> str:
    """Échoue deux fois, puis réussit. Simule un service qui redémarre."""
    # `global` est nécessaire parce qu'on AFFECTE _appels : sans lui,
    # `_appels += 1` créerait une variable locale... lue avant d'exister
    # (UnboundLocalError). Pour juste lire une globale, rien à déclarer.
    global _appels
    _appels += 1
    if _appels < 3:
        print(f"instable : échec {_appels}")
        raise ConnectionError("pas encore prêt")
    print("instable : ok")
    return "connecté"


if __name__ == "__main__":
    # Quand on lance `python3 outils.py`, Python nomme ce module "__main__".
    # Quand un autre fichier fait `import outils`, __name__ vaut "outils" et
    # ce bloc est sauté : la démo ne pollue pas l'importateur. Chapitre 6.
    print(f"1536 octets      → {taille_lisible(1536)}")
    print(f"10485760 octets  → {taille_lisible(10 * 1024 * 1024)}")
    print(parse_kv("host=web01 port=22 user=root"))
    print(slugify("Serveur Web #1 (prod)"))
    retry(instable, essais=5)
