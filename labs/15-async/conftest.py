# conftest.py — convention des labos (voir chapitre 12) :
#   pytest             → teste ton squelette (les modules à la racine du labo)
#   SOLUTION=1 pytest  → teste solution/ (mêmes noms de fichiers, donc mêmes imports)
# Fonctionne avec pytest.ini (--import-mode=importlib), sinon pytest remettrait
# le dossier du labo en tête de sys.path et le squelette gagnerait.
import os
import sys
from pathlib import Path

if os.environ.get("SOLUTION") == "1":
    sys.path.insert(0, str(Path(__file__).parent / "solution"))   # solution/ gagne
