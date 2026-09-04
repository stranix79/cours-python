# banque.py — Labo 09 : un compte bancaire, pour pratiquer classes, dataclasses,
# héritage, propriétés, exceptions et Protocol.
#
# Lance : python3 banque.py  (le bloc if __name__ == "__main__" en bas sert de scénario)

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class SoldeInsuffisant(Exception):
    """Levée quand un retrait dépasse ce que le compte autorise."""
    # TODO : stocker le solde et le montant demandé (attributs), et produire
    #   un message du genre « retrait de 150.00 refusé : solde 100.00 ».
    #   Indice : __init__(self, solde, montant) puis super().__init__(message).


# TODO : transformer Transaction en dataclass GELÉE (frozen=True) avec les champs
#   type ("depot" / "retrait"), montant (float), date (datetime, avec un
#   default_factory=datetime.now) et libelle (str, défaut "").
class Transaction:
    pass


class Compte:
    # Attribut de classe : compteur de comptes créés (sert à générer le numéro).
    _prochain_numero = 1

    def __init__(self, titulaire: str, solde_initial: float = 0.0):
        self.titulaire = titulaire
        # TODO : numéro auto-incrémenté à partir de Compte._prochain_numero
        # TODO : self._solde (privé par convention) et self._historique (liste de Transaction)
        #   Si solde_initial > 0, enregistrer un dépôt initial dans l'historique.
        raise NotImplementedError("TODO")

    # TODO : propriété solde en LECTURE SEULE (pas de setter : on ne modifie le
    #   solde qu'à travers deposer / retirer).

    # TODO : propriété historique qui renvoie une COPIE de la liste (tuple ou list(...))
    #   pour que l'appelant ne puisse pas la modifier de l'extérieur.

    def deposer(self, montant: float, libelle: str = "") -> None:
        # TODO : refuser montant <= 0 (ValueError), sinon créditer et enregistrer.
        raise NotImplementedError("TODO")

    def retirer(self, montant: float, libelle: str = "") -> None:
        # TODO : refuser montant <= 0 (ValueError) ; si montant > solde → SoldeInsuffisant ;
        #   sinon débiter et enregistrer.
        raise NotImplementedError("TODO")

    # TODO : __repr__ : Compte(numero=1, titulaire='Gilles', solde=100.00)
    # TODO : __eq__ : deux comptes sont égaux s'ils ont le même numéro
    #   (n'oublie pas NotImplemented pour un type inconnu).
    # TODO : __len__ : nombre de transactions.

    # TODO : @classmethod depuis_dict(cls, d) : construit un compte depuis
    #   {"titulaire": "...", "solde": 100.0}. Doit marcher aussi pour CompteEpargne
    #   (utilise cls, pas Compte, et **d ou d.get(...) pour les clés en plus).

    # TODO (bonus) : to_json(self) -> str qui sérialise numero, titulaire, solde,
    #   et l'historique (attention : datetime n'est pas sérialisable tel quel,
    #   utilise .isoformat()).


class CompteEpargne(Compte):
    # TODO : __init__(titulaire, solde_initial=0.0, taux=0.02) : appelle super().__init__
    #   puis stocke le taux.
    # TODO : retirer : un compte épargne ne peut pas descendre sous 0 ET on
    #   limite à 3 retraits par mois (compte-les dans l'historique : même mois
    #   et même année que datetime.now()). Au-delà → SoldeInsuffisant ou une
    #   nouvelle exception PlafondRetraits(Exception) : à toi de choisir.
    # TODO : appliquer_interets() : dépose solde * taux avec le libellé "intérêts".
    # TODO : __repr__ incluant le taux.
    pass


class Exportable(Protocol):
    """Tout objet qui sait se sérialiser en JSON."""
    def to_json(self) -> str: ...


def sauvegarder(objets: list[Exportable]) -> None:
    """Affiche le JSON de chaque objet. Ne dépend d'aucune classe concrète."""
    for o in objets:
        print(o.to_json())


if __name__ == "__main__":
    # Scénario : décommente au fur et à mesure que tu implémentes.
    print("Complète les TODO, puis décommente le scénario ci-dessous.")
    # c = Compte("Gilles", 100)
    # c.deposer(50, "salaire")
    # c.retirer(30, "courses")
    # print(c, c.solde, len(c))
    # try:
    #     c.retirer(500)
    # except SoldeInsuffisant as e:
    #     print("refusé :", e)
    # e = CompteEpargne.depuis_dict({"titulaire": "Gilles", "solde": 1000, "taux": 0.03})
    # e.appliquer_interets()
    # print(e)
    # for t in e.historique:
    #     print("  ", t)
    # sauvegarder([c, e])
