# tests/test_cli.py — Labo 20 (solution) : la commande en ligne, testée sans sous-processus.
import pytest

from outils import __version__
from outils.cli import main


def test_version_lue_depuis_les_metadonnees():
    assert __version__ == "0.1.0"


def test_ip_privee(capsys: pytest.CaptureFixture[str]):
    assert main(["ip", "10.1.2.3"]) == 0
    assert capsys.readouterr().out.strip() == "10.1.2.3 : privée"


def test_ip_invalide(capsys: pytest.CaptureFixture[str]):
    assert main(["ip", "pas-une-ip"]) == 1
    assert "invalide" in capsys.readouterr().err


def test_jours(capsys: pytest.CaptureFixture[str]):
    assert main(["jours", "2026-09-07", "2026-09-13"]) == 0
    assert capsys.readouterr().out.strip() == "5 jours ouvrés"
