# inventaire_sqlmodel.py — Labo 18 (partie b) : le même inventaire, avec SQLModel.
#
# Utilisé par : migrer_json.py, test_inventaire.py, et lançable directement.
#
# SQLModel = SQLAlchemy (l'ORM) + pydantic (la validation). Une seule classe
# décrit à la fois la TABLE (colonnes, clés) et l'OBJET Python (types, validation).
# On n'écrit plus de SQL : on manipule des objets, l'ORM génère les requêtes.

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class Serveur(SQLModel, table=True):
    # table=True : cette classe correspond à une table (nom : "serveur", en
    # minuscules, généré depuis le nom de la classe).
    # id est None avant l'insertion (la base l'attribue), d'où `int | None`.
    id: int | None = Field(default=None, primary_key=True)
    nom: str = Field(index=True, unique=True)
    ip: str
    os: str
    cpu: int = 1
    # Relationship : pas une colonne, mais un attribut Python qui donne accès
    # aux services liés. back_populates relie les deux côtés : ajouter un
    # service à serveur.services met à jour service.serveur, et inversement.
    services: list["Service"] = Relationship(back_populates="serveur", cascade_delete=True)


class Service(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nom: str
    port: int
    # La clé étrangère, elle, EST une colonne : "serveur.id" = table.colonne.
    serveur_id: int | None = Field(default=None, foreign_key="serveur.id", ondelete="CASCADE")
    serveur: Serveur | None = Relationship(back_populates="services")


def creer_engine(url: str = "sqlite:///inventaire.db"):
    """Un engine = la connexion (en fait un pool de connexions) vers une base.
    "sqlite://" tout court = base en mémoire, pour les tests.
    Pour PostgreSQL ce serait "postgresql+psycopg://user:mdp@hote/base" :
    seule cette ligne change, tout le reste du fichier reste identique."""
    engine = create_engine(url)
    # Crée les tables de tous les modèles déclarés avec table=True (si absentes).
    SQLModel.metadata.create_all(engine)
    return engine


def ajouter_serveur(session: Session, nom: str, ip: str, os: str, cpu: int = 1) -> Serveur:
    serveur = Serveur(nom=nom, ip=ip, os=os, cpu=cpu)
    session.add(serveur)      # marque l'objet « à insérer »
    session.commit()          # envoie l'INSERT (et tout ce qui est en attente)
    session.refresh(serveur)  # relit la ligne pour récupérer l'id attribué
    return serveur


def ajouter_service(session: Session, serveur: Serveur, nom: str, port: int) -> Service:
    # On passe l'objet Serveur, pas son id : l'ORM remplit serveur_id tout seul.
    service = Service(nom=nom, port=port, serveur=serveur)
    session.add(service)
    session.commit()
    session.refresh(service)
    return service


def serveurs_par_os(session: Session, os: str) -> list[Serveur]:
    # select() construit la requête, session.exec() l'exécute. Serveur.os == os
    # n'est pas un booléen : c'est une expression SQL (WHERE serveur.os = ?),
    # paramétrée, donc sans risque d'injection.
    return list(session.exec(select(Serveur).where(Serveur.os == os).order_by(Serveur.nom)))


def services_de(session: Session, nom_serveur: str) -> list[Service]:
    serveur = session.exec(select(Serveur).where(Serveur.nom == nom_serveur)).first()
    if serveur is None:
        return []
    # La jointure est faite par la Relationship : accéder à .services déclenche
    # un SELECT sur la table service (chargement « paresseux »).
    return sorted(serveur.services, key=lambda s: s.port)


def ports_ouverts(session: Session) -> list[tuple[str, int]]:
    # Ici on veut deux colonnes de deux tables : une vraie jointure explicite.
    requete = select(Serveur.nom, Service.port).join(Service).order_by(Serveur.nom, Service.port)
    return [(nom, port) for nom, port in session.exec(requete)]


def changer_cpu(session: Session, nom: str, cpu: int) -> bool:
    serveur = session.exec(select(Serveur).where(Serveur.nom == nom)).first()
    if serveur is None:
        return False
    serveur.cpu = cpu         # on modifie l'objet...
    session.add(serveur)
    session.commit()          # ...l'ORM génère l'UPDATE des colonnes changées
    return True


def supprimer_serveur(session: Session, nom: str) -> bool:
    serveur = session.exec(select(Serveur).where(Serveur.nom == nom)).first()
    if serveur is None:
        return False
    session.delete(serveur)   # cascade_delete supprime aussi ses services
    session.commit()
    return True


if __name__ == "__main__":
    engine = creer_engine("sqlite://")   # en mémoire pour la démo
    # Une Session = une conversation avec la base : on y fait quelques
    # opérations, puis on la ferme. `with` la ferme même en cas d'erreur.
    with Session(engine) as session:
        web = ajouter_serveur(session, "web-01", "10.0.0.11", "debian", cpu=4)
        ajouter_service(session, web, "nginx", 443)
        ajouter_service(session, web, "sshd", 22)
        db = ajouter_serveur(session, "db-01", "10.0.0.21", "ubuntu", cpu=16)
        ajouter_service(session, db, "postgres", 5432)
        print("debian :", [s.nom for s in serveurs_par_os(session, "debian")])
        print("services de web-01 :", [(s.nom, s.port) for s in services_de(session, "web-01")])
        print("ports :", ports_ouverts(session))
        supprimer_serveur(session, "web-01")
        print("après suppression, services restants :", len(session.exec(select(Service)).all()))
