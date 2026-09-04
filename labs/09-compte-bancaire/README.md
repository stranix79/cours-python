# Labo 09 — Compte bancaire

**Chapitre** : [9. Classes et objets](../../cours/09-classes-et-objets.md)

## Objectif
Écrire une petite hiérarchie de classes complète : dataclass gelée, propriété en lecture seule, exception maison avec attributs, héritage avec `super()`, constructeur alternatif en `@classmethod`, dunders, et un `Protocol`.

## Consignes
1. `Transaction` : une `@dataclass(frozen=True)` avec `type`, `montant`, `date` (défaut `datetime.now` via `default_factory`, pas `datetime.now()`) et `libelle`. Vérifie dans le REPL que deux transactions créées à la suite n'ont pas la même date et qu'on ne peut pas modifier `montant`.
2. `SoldeInsuffisant` : garde `solde` et `montant` en attributs et passe un message lisible à `super().__init__`.
3. `Compte` : numéro auto-incrémenté (attribut de classe), `_solde` et `_historique` créés dans `__init__`, `deposer`/`retirer` avec validation, propriété `solde` **sans setter**, propriété `historique` qui renvoie une copie, `__repr__`, `__eq__` (sur le numéro, avec `NotImplemented`), `__len__`. Puis `depuis_dict` en `@classmethod`, qui doit marcher aussi pour la sous-classe (utilise `cls`).
4. `CompteEpargne(Compte)` : `taux`, `appliquer_interets()`, et `retirer` limité à trois par mois calendaire (compte-les dans l'historique) : lève `PlafondRetraits`. Ne recopie pas la logique du parent, appelle `super().retirer(...)`.
5. Décommente le scénario du `__main__` étape par étape. Compare avec la sortie attendue ci-dessous.
6. Bonus : `to_json()` sur `Compte` (attention à `datetime` : `.isoformat()`), et vérifie que `sauvegarder([c, e])` marche sans que `Compte` hérite d'`Exportable`. C'est ça, un `Protocol`.
7. Bonus 2 : ajoute `__hash__` cohérent avec `__eq__` et vérifie `c in {c}`. Sans `__hash__`, que se passe-t-il quand tu mets un compte dans un `set` ?

## Comment lancer
```bash
source ../../.venv/bin/activate
python3 banque.py
python3 solution/banque.py
python3 -i solution/banque.py     # puis : Compte.__mro__, help(Compte), c.__dict__
```

Sortie attendue de la solution (les dates changent) :
```
Compte(numero=1, titulaire='Gilles', solde=120.00) 120.0 3
refusé : retrait de 500.00 refusé : solde 120.00 | il manque 380.0
lecture seule : property 'solde' of 'Compte' object has no setter
CompteEpargne(numero=2, titulaire='Gilles', solde=1030.00, taux=0.03)
   2026-09-04 13:58 + 1000.00  solde initial
   2026-09-04 13:58 +   30.00  intérêts
plafond : 3 retraits déjà effectués ce mois-ci
False False True
{"numero": 1, "titulaire": "Gilles", "solde": 120.0, "historique": [...]}
{"numero": 2, "titulaire": "Gilles", "solde": 1000.0, "historique": [...]}
```

## Pour aller plus loin
- Les montants en `float` sont une mauvaise idée pour de l'argent (`0.1 + 0.2`). Remplace-les par `decimal.Decimal` et regarde ce que ça change dans `to_json`.
- Réécris `Compte` lui-même en `@dataclass` : `numero` et `_historique` avec `field(init=False)`, et l'initialisation dans `__post_init__`.
- `pydantic.BaseModel` à la place de `dataclass` pour `Transaction` : la validation des types devient automatique. On y revient au chapitre 17.
