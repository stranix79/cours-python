#!/usr/bin/env bash
# verifier.sh — Labo 20 (solution) : rejoue la CI en local.
# Lancé par : bash verifier.sh depuis ce dossier (ou par tools/verifier.sh du cours).
set -eu
cd "$(dirname "$0")"
PY=../../../.venv/bin/python
$PY -m pip install -q -e . >/dev/null          # le src/ layout exige l'installation
$PY -m ruff check .
$PY -m ruff format --check .
$PY -m mypy
$PY -m pytest -p no:cacheprovider
$PY -m build --wheel --sdist --outdir dist . >/dev/null
ls dist/
rm -rf dist src/outils.egg-info .ruff_cache .mypy_cache
echo "Labo 20 : OK"
