#!/usr/bin/env bash
# verifier.sh — Labo 21 (solution) : installe, lint, teste, puis lance l'API
# 5 secondes avec uvicorn et interroge /health et /status.
# Lancé par : bash verifier.sh depuis ce dossier (ou par tools/verifier.sh du cours).
set -eu
cd "$(dirname "$0")"
PY=../../../.venv/bin/python
$PY -m pip install -q -e . >/dev/null
$PY -m ruff check .
$PY -m pytest -p no:cacheprovider

# Lancement réel : base temporaire, worker actif, port libre.
export STATUSBOARD_DATABASE_URL="sqlite:///$(mktemp -d)/sb.db" STATUSBOARD_WORKER=1
PORT=$($PY -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1])')
$PY -m uvicorn statusboard.api:app --port "$PORT" --log-level warning &
PID=$!
trap 'kill $PID 2>/dev/null' EXIT
for i in $(seq 1 30); do curl -sf "http://127.0.0.1:$PORT/health" >/dev/null && break; sleep 0.2; done
curl -sf "http://127.0.0.1:$PORT/health"; echo
TOKEN=$(curl -sf -X POST "http://127.0.0.1:$PORT/token" -d "username=admin&password=admin" | $PY -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')
curl -sf -X POST "http://127.0.0.1:$PORT/targets" -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" -d "{\"name\":\"moi\",\"kind\":\"tcp\",\"address\":\"127.0.0.1:$PORT\",\"interval_s\":1}" >/dev/null
sleep 2.5                                   # le worker a eu le temps de vérifier
curl -sf "http://127.0.0.1:$PORT/status"; echo
curl -sf --max-time 1 -N "http://127.0.0.1:$PORT/events" | head -2 || true
find . -name __pycache__ -exec rm -rf {} + 2>/dev/null; rm -rf src/*.egg-info .ruff_cache
echo "Labo 21 : OK"
