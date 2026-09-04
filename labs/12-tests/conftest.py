# conftest.py — chargé automatiquement par pytest avant les tests.
# Si la variable d'environnement SOLUTION vaut 1, on met solution/ en tête de
# sys.path : « import versions » trouve alors solution/versions.py au lieu du
# squelette. Marche grâce à --import-mode=importlib dans pytest.ini (sinon pytest
# remettrait ce dossier en tête de sys.path au moment d'importer le test).
import os
import sys
from pathlib import Path

if os.environ.get("SOLUTION") == "1":
    sys.path.insert(0, str(Path(__file__).parent / "solution"))
