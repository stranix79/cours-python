# solution/banque.py — Labo 09 : compte bancaire, version complète et commentée.
#
# Rôle : montrer sur un cas classique tout l'attirail du chapitre 9 : classe,
#        dataclass gelée, propriété en lecture seule, exception maison avec
#        attributs, héritage avec super(), classmethod comme constructeur
#        alternatif, dunders (__repr__, __eq__, __len__) et Protocol.
# Lancé par : python3 solution/banque.py (scénario en bas de fichier).

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------
class SoldeInsuffisant(Exception):
    """Levée quand un retrait dépasse ce que le compte autorise."""

    def __init__(self, solde: float, montant: float):
        # On garde les valeurs en attributs : l'appelant peut les exploiter
        # (afficher, proposer un montant, logger) sans parser le message.
        self.solde = solde
        self.montant = montant
        # super().__init__ reçoit le message : c'est lui que str(e) affichera.
        super().__init__(f"retrait de {montant:.2f} refusé : solde {solde:.2f}")


class PlafondRetraits(Exception):
    """Levée quand un compte épargne dépasse son quota de retraits mensuels."""


# ---------------------------------------------------------------------------
# Transaction : une donnée pure, donc une dataclass. Gelée (frozen) parce
# qu'une écriture comptable ne se modifie pas après coup ; en prime, une
# instance gelée est hashable (utilisable dans un set ou comme clé de dict).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Transaction:
    type: str                      # "depot" ou "retrait"
    montant: float
    # default_factory : la fonction est appelée À CHAQUE création, donc chaque
    # transaction a sa propre date. Un simple `date = datetime.now()` serait
    # évalué UNE fois, à la définition de la classe : toutes les transactions
    # auraient la même heure (le piège du défaut mutable, version datetime).
    date: datetime = field(default_factory=datetime.now)
    libelle: str = ""

    def __str__(self) -> str:
        # __repr__ est généré par dataclass (utile au débogage) ; __str__ est
        # ce qu'on montre à un humain dans un relevé.
        signe = "+" if self.type == "depot" else "-"
        return f"{self.date:%Y-%m-%d %H:%M} {signe}{self.montant:8.2f}  {self.libelle}"


# ---------------------------------------------------------------------------
# Compte
# ---------------------------------------------------------------------------
class Compte:
    # Attribut de CLASSE : un seul compteur, partagé. C'est exactement ce qu'on
    # veut ici (numéros uniques), contrairement au piège de la liste partagée.
    _prochain_numero = 1

    def __init__(self, titulaire: str, solde_initial: float = 0.0):
        self.titulaire = titulaire
        self.numero = Compte._prochain_numero
        Compte._prochain_numero += 1
        # Underscore : « détail interne, passe par les méthodes ». L'interpréteur
        # ne l'interdit pas, mais tout lecteur Python comprend l'intention.
        self._solde = 0.0
        self._historique: list[Transaction] = []   # créé ICI, par instance
        if solde_initial > 0:
            self.deposer(solde_initial, "solde initial")

    # Propriété en lecture seule : pas de @solde.setter, donc c.solde = 5 lève
    # AttributeError. Le solde ne bouge que par deposer/retirer, qui tiennent
    # l'historique à jour. C'est l'invariant que la classe protège.
    @property
    def solde(self) -> float:
        return self._solde

    # On renvoie un tuple (copie immuable) : l'appelant peut lire, itérer,
    # mais pas faire compte.historique.append(...) ni .clear().
    @property
    def historique(self) -> tuple[Transaction, ...]:
        return tuple(self._historique)

    def deposer(self, montant: float, libelle: str = "") -> None:
        if montant <= 0:
            raise ValueError(f"montant invalide : {montant}")
        self._solde += montant
        self._historique.append(Transaction("depot", montant, libelle=libelle))

    def retirer(self, montant: float, libelle: str = "") -> None:
        if montant <= 0:
            raise ValueError(f"montant invalide : {montant}")
        if montant > self._solde:
            raise SoldeInsuffisant(self._solde, montant)
        self._solde -= montant
        self._historique.append(Transaction("retrait", montant, libelle=libelle))

    # type(self).__name__ plutôt que "Compte" en dur : une sous-classe qui ne
    # redéfinit pas __repr__ s'affichera quand même sous son vrai nom.
    def __repr__(self) -> str:
        return (f"{type(self).__name__}(numero={self.numero}, "
                f"titulaire={self.titulaire!r}, solde={self._solde:.2f})")

    def __eq__(self, autre: object) -> bool:
        if not isinstance(autre, Compte):
            return NotImplemented          # laisse Python essayer l'autre opérande
        return self.numero == autre.numero

    # Définir __eq__ sans __hash__ rend la classe non hashable (Python met
    # __hash__ à None). On le rétablit sur le numéro, cohérent avec __eq__.
    def __hash__(self) -> int:
        return hash(self.numero)

    def __len__(self) -> int:
        return len(self._historique)

    # Constructeur alternatif. cls est la classe sur laquelle on a appelé la
    # méthode : Compte.depuis_dict → Compte, CompteEpargne.depuis_dict → CompteEpargne.
    # C'est ce qui rend le classmethod héritable, contrairement à un Compte(...) en dur.
    @classmethod
    def depuis_dict(cls, d: dict) -> "Compte":
        # On copie et on extrait les clés communes ; ce qui reste (taux, ...)
        # est passé tel quel à __init__ de la sous-classe avec **.
        d = dict(d)
        titulaire = d.pop("titulaire")
        solde = d.pop("solde", 0.0)
        return cls(titulaire, solde, **d)

    def to_json(self) -> str:
        # datetime n'est pas sérialisable par json : on le convertit en texte
        # ISO 8601 ("2026-09-04T14:03:12.123456"), lisible et re-parsable.
        return json.dumps({
            "numero": self.numero,
            "titulaire": self.titulaire,
            "solde": round(self._solde, 2),
            "historique": [
                {"type": t.type, "montant": t.montant,
                 "date": t.date.isoformat(), "libelle": t.libelle}
                for t in self._historique
            ],
        }, ensure_ascii=False)


# ---------------------------------------------------------------------------
# CompteEpargne : « est un » Compte (on peut le passer partout où un Compte
# est attendu), avec une règle de retrait plus stricte et des intérêts.
# ---------------------------------------------------------------------------
class CompteEpargne(Compte):
    RETRAITS_MAX_PAR_MOIS = 3           # constante de classe, partagée, non mutable

    def __init__(self, titulaire: str, solde_initial: float = 0.0, taux: float = 0.02):
        super().__init__(titulaire, solde_initial)   # numéro, solde, historique
        self.taux = taux

    def retirer(self, montant: float, libelle: str = "") -> None:
        maintenant = datetime.now()
        # Compte les retraits du mois courant dans l'historique.
        ce_mois = sum(
            1 for t in self._historique
            if t.type == "retrait"
            and (t.date.year, t.date.month) == (maintenant.year, maintenant.month)
        )
        if ce_mois >= self.RETRAITS_MAX_PAR_MOIS:
            raise PlafondRetraits(
                f"{self.RETRAITS_MAX_PAR_MOIS} retraits déjà effectués ce mois-ci")
        # La règle « pas sous zéro » et l'enregistrement sont déjà dans le parent :
        # on délègue au lieu de recopier.
        super().retirer(montant, libelle)

    def appliquer_interets(self) -> None:
        interets = round(self._solde * self.taux, 2)
        if interets > 0:
            self.deposer(interets, "intérêts")

    def __repr__(self) -> str:
        # On réutilise le repr du parent et on glisse le taux avant la parenthèse.
        return super().__repr__()[:-1] + f", taux={self.taux})"


# ---------------------------------------------------------------------------
# Protocol : « tout ce qui a une méthode to_json() -> str ». Compte est conforme
# sans hériter d'Exportable ; un Rapport, un Hote, n'importe quoi le serait aussi.
# ---------------------------------------------------------------------------
class Exportable(Protocol):
    def to_json(self) -> str: ...


def sauvegarder(objets: list[Exportable]) -> None:
    for o in objets:
        print(o.to_json())


if __name__ == "__main__":
    c = Compte("Gilles", 100)
    c.deposer(50, "salaire")
    c.retirer(30, "courses")
    print(c, c.solde, len(c))

    try:
        c.retirer(500)
    except SoldeInsuffisant as e:
        print("refusé :", e, "| il manque", e.montant - e.solde)

    try:
        c.solde = 1_000_000
    except AttributeError as e:
        print("lecture seule :", e)

    e = CompteEpargne.depuis_dict({"titulaire": "Gilles", "solde": 1000, "taux": 0.03})
    e.appliquer_interets()
    print(e)
    for t in e.historique:
        print("  ", t)

    for i in range(4):
        try:
            e.retirer(10, f"retrait {i + 1}")
        except PlafondRetraits as err:
            print("plafond :", err)

    print(c == e, c == Compte.depuis_dict({"titulaire": "X"}), c in {c})
    sauvegarder([c, e])
