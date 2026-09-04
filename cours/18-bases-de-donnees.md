# 18. Bases de données : sqlite3, SQLAlchemy, SQLModel

*Python de zéro à FastAPI — chapitre 18 sur 21.* ← [17. FastAPI : premiers pas](17-fastapi-premiers-pas.md) · [Sommaire](../README.md) · [19. FastAPI avancé : dépendances, auth, tests, Docker](19-fastapi-avance.md) →

> 🧪 Labo associé : [`labs/18-sqlite-sqlmodel`](../labs/18-sqlite-sqlmodel/README.md)

L'API du labo 17 oublie tout quand on l'arrête. Et le carnet d'adresses du labo 07 dans un fichier JSON fonctionne très bien… jusqu'à ce que deux processus écrivent dedans en même temps, ou qu'on veuille « tous les serveurs Debian avec un port 22 ouvert » sans tout charger en mémoire. C'est le boulot d'une base de données.

### 18.1 Pourquoi une base plutôt qu'un fichier

Un fichier JSON, c'est : tout lire, tout modifier en mémoire, tout réécrire. Trois problèmes apparaissent dès que ça grossit ou que plusieurs clients s'en servent :

| Problème | Fichier JSON | Base de données |
|---|---|---|
| **Concurrence** : deux écritures en même temps | l'une écrase l'autre, ou fichier corrompu | transactions, verrous, les deux passent ou l'une attend |
| **Requêtes** : « les serveurs Debian avec plus de 8 CPU, triés par nom » | charger tout, filtrer en Python | `SELECT … WHERE … ORDER BY`, avec un index, en millisecondes |
| **Intégrité** : un service qui pointe vers un serveur supprimé | rien ne l'empêche | clés étrangères, contraintes `UNIQUE`, `NOT NULL` |
| **Durabilité** : coupure de courant pendant l'écriture | fichier à moitié écrit | soit la transaction est écrite, soit elle ne l'est pas |

Le langage pour parler à une base relationnelle s'appelle **SQL**. Il a cinquante ans et il est partout : SQLite, PostgreSQL, MySQL, SQL Server, Oracle parlent tous le même SQL à 90 %.

### 18.2 SQL en vingt lignes

Ce dont tu as besoin pour ce cours, et pour 80 % de la vie :

```sql
CREATE TABLE serveurs (
    id  INTEGER PRIMARY KEY,          -- auto-attribué
    nom TEXT    NOT NULL UNIQUE,
    ip  TEXT    NOT NULL,
    cpu INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE services (
    id         INTEGER PRIMARY KEY,
    serveur_id INTEGER NOT NULL REFERENCES serveurs(id),   -- clé étrangère
    nom        TEXT    NOT NULL,
    port       INTEGER NOT NULL
);
CREATE INDEX idx_services_serveur ON services(serveur_id);  -- accélère les jointures

INSERT INTO serveurs (nom, ip, cpu) VALUES ('web-01', '10.0.0.11', 4);
SELECT nom, cpu FROM serveurs WHERE cpu >= 4 ORDER BY nom;
UPDATE serveurs SET cpu = 8 WHERE nom = 'web-01';
DELETE FROM serveurs WHERE nom = 'web-01';

-- La jointure : « les ports de web-01 », en reliant les deux tables par la clé étrangère.
SELECT services.nom, services.port
FROM services JOIN serveurs ON serveurs.id = services.serveur_id
WHERE serveurs.nom = 'web-01';
```

Une **table** est un tableau typé avec des colonnes ; une **ligne** est un enregistrement ; la **clé primaire** identifie une ligne ; une **clé étrangère** pointe vers la clé primaire d'une autre table, c'est ainsi qu'on modélise « un serveur a plusieurs services » ; un **index** est une structure annexe qui rend les `WHERE` et les `JOIN` sur cette colonne rapides, au prix d'écritures un peu plus lentes.

> **Venant du C** : une table est un tableau de structs, sauf qu'il vit sur disque, qu'il a des contraintes, et que quelqu'un a déjà écrit pour toi la recherche, le tri, la jointure et le verrouillage. Le SQL est déclaratif : tu dis *ce que* tu veux, le moteur décide *comment* (quel index, quel ordre de jointure).

### 18.3 SQLite : une base dans un fichier

SQLite est une base complète, dans une bibliothèque C d'un mégaoctet, qui stocke tout dans **un seul fichier**. Pas de serveur, pas de port, pas de mot de passe. C'est la base la plus déployée au monde (chaque téléphone, chaque navigateur, chaque Mac en a des dizaines), et Python l'embarque dans la bibliothèque standard : `import sqlite3`. Pour un outil en ligne de commande, un cache, une petite API, un prototype : c'est le bon choix, et souvent le choix définitif.

```python
import sqlite3

con = sqlite3.connect("inventaire.db")     # crée le fichier s'il n'existe pas ; ":memory:" pour une base en RAM
con.execute("CREATE TABLE IF NOT EXISTS serveurs (id INTEGER PRIMARY KEY, nom TEXT NOT NULL UNIQUE, ip TEXT, cpu INTEGER)")

con.execute("INSERT INTO serveurs (nom, ip, cpu) VALUES (?, ?, ?)", ("web-01", "10.0.0.11", 4))
con.executemany("INSERT INTO serveurs (nom, ip, cpu) VALUES (?, ?, ?)",
                [("db-01", "10.0.0.21", 16), ("web-02", "10.0.0.12", 4)])
con.commit()                                # rien n'est écrit tant qu'on n'a pas commit

cur = con.execute("SELECT nom, cpu FROM serveurs WHERE cpu >= ? ORDER BY nom", (4,))
print(cur.fetchall())                       # [('db-01', 16), ('web-01', 4), ('web-02', 4)]
```

Ce qu'il faut voir :

- **`execute(sql, paramètres)`**. Les `?` sont remplacés par les valeurs du tuple, **par SQLite**, avec l'échappement qui va bien. Note le `(4,)` : un tuple d'un élément a besoin de sa virgule (chapitre 4).
- **`commit()`**. `sqlite3` ouvre une transaction au premier `INSERT`/`UPDATE`/`DELETE` et ne l'écrit qu'au `commit()`. Oublie-le et tu fermes la connexion avec une base vide. `with con:` fait le commit à la sortie du bloc (ou un rollback si une exception sort du bloc) ; attention, ça ne ferme pas la connexion, c'est `con.close()`.
- **`fetchall()` / `fetchone()`**, ou itérer sur le curseur. Par défaut, une ligne est un tuple. Avec `con.row_factory = sqlite3.Row`, on accède par nom : `row["nom"]`, et `dict(row)` la convertit.
- **`executescript()`** pour plusieurs ordres d'un coup (le schéma) ; `execute()` n'en accepte qu'un.
- Les erreurs sont des exceptions : `sqlite3.IntegrityError: UNIQUE constraint failed: serveurs.nom` si tu insères deux fois `web-01`.

> **Piège** : SQLite n'applique **pas** les clés étrangères par défaut, pour rester compatible avec des fichiers de 2005. `con.execute("PRAGMA foreign_keys = ON")` juste après `connect()`, sinon `ON DELETE CASCADE` et `REFERENCES` sont décoratifs.

Et en ligne de commande, `sqlite3 inventaire.db` (installé sur macOS et la plupart des Linux) ouvre un shell : `.tables`, `.schema serveurs`, `SELECT * FROM serveurs;`, `.quit`. Indispensable pour regarder ce que ton script a vraiment écrit.

### 18.4 L'injection SQL, ou pourquoi jamais de f-string dans du SQL

```python
nom = "x' OR '1'='1"                                        # ce qu'un utilisateur malveillant tape
con.execute(f"SELECT nom FROM serveurs WHERE nom = '{nom}'").fetchall()   # → TOUS les serveurs
con.execute("SELECT nom FROM serveurs WHERE nom = ?", (nom,)).fetchall()  # → []
```

Avec la f-string, la requête devient `WHERE nom = 'x' OR '1'='1'`, toujours vraie. Avec `'; DROP TABLE serveurs; --`, c'est la table qui disparaît. Ce trou est vieux comme le web et il est encore dans le top 3 des failles chaque année. La règle n'a pas d'exception : **les données passent par les paramètres, jamais par la chaîne**. Le seul cas où on assemble du SQL en Python, c'est pour le nom d'une table ou d'une colonne, et alors la valeur vient d'une liste blanche à toi, pas de l'extérieur.

### 18.5 L'ORM : des objets, pas des lignes

Écrire du SQL à la main marche, mais le code se remplit vite de « je lis une ligne, j'en fais un objet, je modifie l'objet, j'écris l'UPDATE colonne par colonne ». Un **ORM** (*Object-Relational Mapper*) automatise cette traduction : une classe = une table, une instance = une ligne, un attribut = une colonne. Tu manipules des objets, il génère le SQL.

En Python, l'ORM de référence est **SQLAlchemy** (2006, réécrit en 2.0 en 2023). Il a deux étages : le *Core* (construire du SQL avec des objets Python, sans écrire de chaînes) et l'*ORM* par-dessus. Un aperçu, pour reconnaître le style quand tu le croiseras :

```python
from sqlalchemy import create_engine, select, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase): ...

class Serveur(Base):
    __tablename__ = "serveurs"
    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(64), unique=True)
    cpu: Mapped[int] = mapped_column(default=1)

engine = create_engine("sqlite:///inventaire.db")
Base.metadata.create_all(engine)
with Session(engine) as session:
    session.add(Serveur(nom="web-01", cpu=4))
    session.commit()
    gros = session.scalars(select(Serveur).where(Serveur.cpu >= 4)).all()
```

C'est puissant, c'est verbeux, et ça ne valide rien : `Serveur(cpu="quatre")` passe jusqu'à la base.

### 18.6 SQLModel : SQLAlchemy + pydantic

**SQLModel** est écrit par l'auteur de FastAPI. Une classe SQLModel est à la fois un modèle pydantic (validation, sérialisation JSON, chapitre 17) et un modèle SQLAlchemy (table, requêtes). Un seul modèle pour la table **et** l'API, et exactement la syntaxe que tu connais déjà :

```python
from sqlmodel import SQLModel, Field, Relationship, Session, create_engine, select

class Serveur(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)   # None avant l'INSERT
    nom: str = Field(index=True, unique=True)
    ip: str
    cpu: int = 1
    services: list["Service"] = Relationship(back_populates="serveur")

class Service(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nom: str
    port: int
    serveur_id: int | None = Field(default=None, foreign_key="serveur.id")
    serveur: Serveur | None = Relationship(back_populates="services")
```

- `table=True` : cette classe est une table (sans, c'est un modèle pydantic ordinaire, utile pour les schémas d'API). Le nom de table est le nom de classe en minuscules : `serveur`, `service`.
- `Field(...)` est celui de pydantic, enrichi : `primary_key`, `index`, `unique`, `foreign_key="table.colonne"`.
- `Relationship` n'est **pas** une colonne. C'est l'attribut Python qui donne accès aux objets liés : `serveur.services` est la liste de ses services, `service.serveur` son serveur. `back_populates` relie les deux sens. La clé étrangère, elle, est une colonne, c'est `serveur_id`.

Le CRUD :

```python
engine = create_engine("sqlite://")           # "sqlite://" = en mémoire ; "sqlite:///fichier.db" = fichier
SQLModel.metadata.create_all(engine)          # crée les tables de tous les modèles table=True

with Session(engine) as session:
    web = Serveur(nom="web-01", ip="10.0.0.11", cpu=4)
    session.add(web)                          # à insérer
    session.commit()                          # INSERT envoyé
    session.refresh(web)                      # relit la ligne : web.id vaut maintenant 1

    session.add(Service(nom="nginx", port=443, serveur=web))   # serveur_id rempli tout seul
    session.add(Service(nom="sshd", port=22, serveur=web))
    session.commit()

    gros = session.exec(select(Serveur).where(Serveur.cpu >= 4)).all()   # [Serveur(cpu=4, nom='web-01', ...)]
    un = session.get(Serveur, 1)              # par clé primaire, None si absent
    [s.nom for s in web.services]             # ['nginx', 'sshd'] : un SELECT déclenché à l'accès
    session.exec(select(Service).where(Service.port == 22)).one().serveur.nom   # 'web-01'
    session.exec(select(Service.nom, Serveur.nom).join(Serveur)).all()   # [('nginx', 'web-01'), ('sshd', 'web-01')]

    web.cpu = 8
    session.add(web); session.commit()        # UPDATE serveur SET cpu=8 WHERE id=1
    session.delete(un); session.commit()      # DELETE
```

`Serveur.cpu >= 4` n'est pas un booléen : c'est une expression SQL. `print(select(Serveur).where(Serveur.cpu >= 4))` affiche `SELECT … FROM serveur WHERE serveur.cpu >= :cpu_1` : paramétré, donc sans injection possible. `create_engine(url, echo=True)` fait défiler tout le SQL généré, ce qui est la meilleure façon d'apprendre ce que l'ORM fait dans ton dos.

La **Session** est l'unité de travail : une conversation avec la base. On y ajoute, modifie, supprime des objets, et `commit()` envoie tout d'un coup dans une transaction. Une session par requête HTTP, c'est la règle qu'on appliquera au chapitre 19 avec `Depends`.

> **Venant de Java** : c'est JPA/Hibernate, avec `@Entity` remplacé par `table=True`, `@Id` par `primary_key=True`, `@OneToMany` par `Relationship`, et l'`EntityManager` par la `Session`. Les mêmes concepts, et les mêmes pièges (le chargement paresseux, le N+1).

### 18.7 Ce qui reste à savoir

**Transactions.** Tout ce qui est entre le début et `commit()` est atomique : soit tout, soit rien. Importer 100 000 lignes avec un `commit()` par ligne prend des minutes (chaque commit force une écriture disque), avec un seul à la fin, une seconde. Si une exception sort du `with Session(...)`, la session fait un rollback.

**Le N+1.** Charger 100 serveurs puis accéder à `serveur.services` pour chacun déclenche 1 + 100 requêtes ; la solution s'appelle le chargement anticipé (`selectinload`), à connaître quand une page devient lente.

**Pool de connexions.** L'`engine` ne tient pas une connexion, il en gère un réservoir. On crée un engine par application, jamais un par requête.

**Changer de base.** `create_engine("postgresql+psycopg://user:mdp@hote:5432/base")` et `pip install psycopg`, et tout le reste du code est identique. C'est la vraie valeur de l'ORM : SQLite en dev et en test, PostgreSQL en prod, sans réécriture. Le même principe vaut pour MySQL (`mysql+pymysql://`).

> **Migrations.** `create_all()` crée les tables manquantes, mais ne modifie jamais une table existante : ajouter une colonne à `Serveur` après la mise en production ne fait rien à la base. L'outil pour ça s'appelle **Alembic** : il compare tes modèles au schéma réel, génère un script « ajouter la colonne X », versionné, rejouable en prod. Tu n'en as pas besoin pour ce cours, mais le jour où tu modifies un modèle sur une base qui contient des données, c'est lui.

### 18.8 Ce qu'il faut retenir

- Une base relationnelle apporte concurrence, requêtes, intégrité et durabilité, ce qu'un fichier JSON n'a pas.
- SQLite : une base complète dans un fichier, sans serveur, dans la stdlib. Souvent suffisante.
- `sqlite3` : `connect`, `execute(sql, params)`, `commit`, `fetchall`, `row_factory = sqlite3.Row`, `PRAGMA foreign_keys = ON`.
- **Jamais de f-string dans du SQL** : les paramètres `?` sont la seule protection contre l'injection.
- SQLModel : une classe = une table + un modèle pydantic. `Session`, `add`, `commit`, `refresh`, `select().where()`, `Relationship`.
- L'ORM te libère de SQLite pour PostgreSQL en changeant une URL. `echo=True` pour voir le SQL généré.

**Labo 18** : le même inventaire de serveurs et de services écrit en `sqlite3` pur puis en SQLModel, plus un script qui importe un JSON dans la base.

---

← [17. FastAPI : premiers pas](17-fastapi-premiers-pas.md) · [Sommaire](../README.md) · [19. FastAPI avancé : dépendances, auth, tests, Docker](19-fastapi-avance.md) →
