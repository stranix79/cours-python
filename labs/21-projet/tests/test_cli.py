# tests/test_cli.py — Labo 21 : la CLI avec le CliRunner de typer.
from typer.testing import CliRunner

from statusboard.cli import app

runner = CliRunner()


def test_add_puis_list(client: object) -> None:  # `client` : pour la base initialisée
    r = runner.invoke(app, ["add", "dns", "tcp", "1.1.1.1:53", "-i", "10"])
    assert r.exit_code == 0, r.output
    assert "ajouté : dns" in r.output
    assert runner.invoke(app, ["add", "dns", "tcp", "1.1.1.1:53"]).exit_code == 1
    r = runner.invoke(app, ["list"])
    assert "dns" in r.output and "1.1.1.1:53" in r.output
    r = runner.invoke(app, ["status"])
    assert r.output.startswith("?")
