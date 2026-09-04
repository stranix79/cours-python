# Dockerfile — Labo 19 : l'API dans un conteneur.
#   docker build -t tickets-api .
#   docker run --rm -p 8000:8000 tickets-api

# ---------- étape 1 : construire les dépendances ----------
FROM python:3.13-slim AS builder
WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- étape 2 : l'image finale ----------
FROM python:3.13-slim
# TODO : créer un utilisateur non-root (useradd --create-home --uid 1000 api) et
#        passer dessus avec USER avant le CMD. Jamais root dans un conteneur.
WORKDIR /home/api
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TICKETS_DATABASE_URL=sqlite:////data/tickets.db
COPY app ./app
RUN mkdir -p /data
EXPOSE 8000
# TODO : un HEALTHCHECK qui appelle http://127.0.0.1:8000/health
#        (python -c "import urllib.request..." : pas de curl dans l'image slim).
# TODO : CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
#        Pourquoi 0.0.0.0 et pas 127.0.0.1 ?
