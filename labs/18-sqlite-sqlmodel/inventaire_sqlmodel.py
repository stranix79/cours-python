# inventaire_sqlmodel.py — Labo 18 (partie b) : le même inventaire avec SQLModel.
# Une classe = une table ET un objet Python validé. Plus de SQL écrit à la main.

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class Serveur(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)   # None avant l'INSERT
    nom: str = Field(index=True, unique=True)
    ip: str
    os: str
    cpu: int = 1
    # Pas une colonne : l'accès aux services liés. cascade_delete : supprimer
    # le serveur supprime ses services.
    # TODO : ajoute back_populates="serveur" une fois la relation inverse écrite dans Service.
    services: list["Service"] = Relationship(cascade_delete=True)


class Service(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nom: str
    port: int
    # La clé étrangère, elle, est une vraie colonne : "serveur.id" = table.colonne.
    serveur_id: int | None = Field(default=None, foreign_key="serveur.id", ondelete="CASCADE")
    # TODO : la relation inverse, pour écrire service.serveur :
    #   serveur: Serveur | None = Relationship(back_populates="services")


def creer_engine(url: str = "sqlite:///inventaire.db"):
    """"sqlite://" = base en mémoire (tests). Pour PostgreSQL, seule cette URL changerait."""
    engine = create_engine(url)
    SQLModel.metadata.create_all(engine)   # crée les tables manquantes
    return engine


def ajouter_serveur(session: Session, nom: str, ip: str, os: str, cpu: int = 1) -> Serveur:
    serveur = Serveur(nom=nom, ip=ip, os=os, cpu=cpu)
    session.add(serveur)      # à insérer
    session.commit()          # envoie l'INSERT
    session.refresh(serveur)  # récupère l'id attribué par la base
    return serveur


def ajouter_service(session: Session, serveur: Serveur, nom: str, port: int) -> Service:
    # TODO : Service(nom=..., port=..., serveur=serveur) puis add / commit / refresh
    raise NotImplementedError("TODO")


def serveurs_par_os(session: Session, os: str) -> list[Serveur]:
    # TODO : session.exec(select(Serveur).where(Serveur.os == os).order_by(Serveur.nom))
    raise NotImplementedError("TODO")


def services_de(session: Session, nom_serveur: str) -> list[Service]:
    """Les services du serveur, triés par port ; [] si le serveur n'existe pas."""
    # TODO : trouve le serveur (select ... .first()), puis serveur.services (la Relationship
    #   fait la jointure), trié avec sorted(..., key=lambda s: s.port)
    raise NotImplementedError("TODO")


def ports_ouverts(session: Session) -> list[tuple[str, int]]:
    # TODO : select(Serveur.nom, Service.port).join(Service).order_by(Serveur.nom, Service.port)
    raise NotImplementedError("TODO")


def changer_cpu(session: Session, nom: str, cpu: int) -> bool:
    # TODO : trouver, modifier l'attribut, add, commit
    raise NotImplementedError("TODO")


def supprimer_serveur(session: Session, nom: str) -> bool:
    # TODO : trouver, session.delete(obj), commit
    raise NotImplementedError("TODO")


if __name__ == "__main__":
    engine = creer_engine("sqlite://")
    with Session(engine) as session:
        web = ajouter_serveur(session, "web-01", "10.0.0.11", "debian", cpu=4)
        print(web)
        # TODO : ajoute des services, affiche services_de et ports_ouverts
