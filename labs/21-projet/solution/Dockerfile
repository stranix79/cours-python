# Dockerfile — Labo 21 (solution) : l'API statusboard dans un conteneur.
#
#   docker build -t statusboard .
#   docker run --rm -p 8000:8000 -e STATUSBOARD_SECRET_KEY=... statusboard
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
# ping n'est pas dans l'image slim ; iputils-ping l'apporte, et on nettoie le cache apt.
RUN apt-get update && apt-get install -y --no-install-recommends iputils-ping \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 app
WORKDIR /app
# Dépendances d'abord (couche mise en cache tant que pyproject.toml ne change pas).
COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir .
# La base SQLite vit dans /data, monté en volume par docker-compose.
RUN mkdir /data && chown app:app /data
ENV STATUSBOARD_DATABASE_URL=sqlite:////data/statusboard.db
USER app
EXPOSE 8000
CMD ["uvicorn", "statusboard.api:app", "--host", "0.0.0.0", "--port", "8000"]
