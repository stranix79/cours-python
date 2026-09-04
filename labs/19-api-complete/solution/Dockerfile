# Dockerfile — Labo 19 : l'API dans un conteneur.
#
# Construire : docker build -t tickets-api .
# Lancer     : docker run --rm -p 8000:8000 -e TICKETS_SECRET_KEY=... tickets-api
#
# Deux étapes (« multi-stage ») : la première installe les dépendances avec les
# outils de compilation, la seconde ne garde que le résultat. L'image finale
# est plus petite et ne contient ni pip ni compilateur.

# ---------- étape 1 : construire les dépendances ----------
FROM python:3.13-slim AS builder
WORKDIR /build
# Un venv dans l'image, pour pouvoir le copier tel quel dans l'étape 2.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
# On copie requirements.txt SEUL d'abord : tant qu'il ne change pas, Docker
# réutilise cette couche en cache et ne réinstalle rien à chaque modification du code.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- étape 2 : l'image finale ----------
FROM python:3.13-slim
# Jamais root dans un conteneur : si l'app est compromise, l'attaquant n'est
# qu'un utilisateur sans droits.
RUN useradd --create-home --uid 1000 api
WORKDIR /home/api
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    # Pas de .pyc sur disque, et les logs sortent tout de suite (pas de tampon).
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # La base dans /data : un volume monté par docker-compose pour survivre au conteneur.
    TICKETS_DATABASE_URL=sqlite:////data/tickets.db
COPY --chown=api:api app ./app
RUN mkdir -p /data && chown api:api /data
USER api
EXPOSE 8000
# Docker interroge /health ; un conteneur « unhealthy » est redémarré par
# l'orchestrateur ou signalé dans `docker ps`.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status == 200 else 1)"
# 0.0.0.0 : écouter sur toutes les interfaces du conteneur, sinon rien n'est
# joignable depuis l'extérieur. --proxy-headers : faire confiance aux en-têtes
# X-Forwarded-* du reverse proxy devant (nginx, traefik).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
