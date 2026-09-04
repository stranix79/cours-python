# Labo 18 — Un inventaire de serveurs qui survit au redémarrage

**Chapitre** : [18. Bases de données : sqlite3, SQLAlchemy, SQLModel](../../cours/18-bases-de-donnees.md)

## Objectif
Le même inventaire (serveurs et leurs services) écrit deux fois : en SQL à la main avec `sqlite3`, puis avec l'ORM SQLModel. Plus un script qui importe un JSON dans la base.

## Consignes
1. **Partie a, `inventaire_sqlite.py`** : complète le schéma (table `services` avec clé étrangère `ON DELETE CASCADE` et un index), puis les fonctions marquées `TODO`. Toutes les requêtes utilisent des paramètres `?` : le test `test_sqlite_injection_impossible` vérifie qu'un nom piégé ne renvoie rien.
2. Lance `python3 inventaire_sqlite.py`, puis ouvre une vraie base : `python3 -c "import inventaire_sqlite as s; s.ouvrir('inventaire.db')"` et inspecte-la avec `sqlite3 inventaire.db` (`.tables`, `.schema serveurs`, `SELECT * FROM serveurs;`).
3. **Partie b, `inventaire_sqlmodel.py`** : ajoute la clé étrangère et la relation dans `Service`, puis les mêmes fonctions avec `select()`, `.where()`, `.join()` et les relations. Compare ligne à ligne avec la partie a : où est passé le SQL ? Mets `create_engine(url, echo=True)` pour le voir défiler.
4. **`migrer_json.py`** : importe `serveurs.json` dans `inventaire.db`. Relance : rien ne doit être importé en double.
5. `pytest` : 10 tests, les mêmes scénarios pour les deux implémentations, plus la migration. Note comment les tests `sqlite3` utilisent `tmp_path` (une vraie base fichier, jetable) et ceux de SQLModel une base en mémoire (`sqlite://`).
6. Bonus : ajoute `serveurs_sans_ssh(session)` (les serveurs qui n'ont aucun service sur le port 22). Il faut un `outerjoin` ou une sous-requête : cherche `select(...).where(~Serveur.services.any(Service.port == 22))`.

## Comment lancer
```bash
source ../../.venv/bin/activate
python3 inventaire_sqlite.py
python3 inventaire_sqlmodel.py
python3 migrer_json.py serveurs.json          # crée inventaire.db
sqlite3 inventaire.db "SELECT serveur.nom, service.port FROM service JOIN serveur ON serveur.id = service.serveur_id"
pytest                                        # ton squelette
SOLUTION=1 pytest                             # la solution
rm -f inventaire.db                           # la base est gitignorée, mais autant nettoyer
```

Sortie attendue de `python3 solution/inventaire_sqlmodel.py` :

```
debian : ['web-01']
services de web-01 : [('sshd', 22), ('nginx', 443)]
ports : [('db-01', 5432), ('web-01', 22), ('web-01', 443)]
après suppression, services restants : 1
```

## Pour aller plus loin
- Enlève `PRAGMA foreign_keys = ON` dans `ouvrir()` et relance les tests : lequel casse, et pourquoi SQLite est-il comme ça ?
- Ajoute 100 000 serveurs en boucle avec un `commit()` par ligne, puis un seul à la fin. Chronomètre (`time.perf_counter()`). C'est la raison d'être des transactions.
- `pip install alembic` et `alembic init migrations` : regarde ce qu'il génère, sans aller plus loin. C'est l'outil qu'on utilise quand le schéma change après la mise en production.
