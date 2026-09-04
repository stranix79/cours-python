# tests/test_reseau.py — Labo 20 : tests du module reseau.
from outils import reseau


def test_ip_valide():
    assert reseau.est_ip_valide("192.168.1.10")
    assert reseau.est_ip_valide("::1")
    assert not reseau.est_ip_valide("192.168.1.256")
    assert not reseau.est_ip_valide("hawking")


def test_ip_privee():
    assert reseau.est_privee("10.0.0.1")
    assert not reseau.est_privee("8.8.8.8")


def test_decouper_url():
    assert reseau.decouper_url("https://stranix.net/blog") == (
        "https",
        "stranix.net",
        443,
        "/blog",
    )
    assert reseau.decouper_url("http://localhost:8000") == (
        "http",
        "localhost",
        8000,
        "/",
    )


def test_masque_vers_prefixe():
    assert reseau.masque_vers_prefixe("255.255.255.0") == 24
    assert reseau.masque_vers_prefixe("255.255.0.0") == 16


def test_port_ferme():
    # Rien n'écoute normalement sur le port 9 de la boucle locale (discard).
    assert reseau.port_ouvert("127.0.0.1", 9, timeout=0.2) is False
