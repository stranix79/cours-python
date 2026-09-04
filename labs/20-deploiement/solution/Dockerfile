# Dockerfile — Labo 20 (solution) : image de la commande `outils`.
#
# Deux étapes : la première construit la wheel (elle a besoin de `build` et de
# hatchling), la seconde ne contient que Python, la wheel installée et un
# utilisateur non privilégié.
#
#   docker build -t outils .
#   docker run --rm outils ip 10.0.0.1

# ---- Étape 1 : construire la wheel ------------------------------------------
FROM python:3.13-slim AS build
WORKDIR /src
# D'abord les métadonnées : cette couche (et le pip install qui suit) n'est
# refaite que si pyproject.toml change.
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir build
# Ensuite le code, puis la construction.
COPY src/ src/
RUN python -m build --wheel --outdir /dist

# ---- Étape 2 : l'image finale -----------------------------------------------
FROM python:3.13-slim
# Pas de __pycache__ écrits dans le conteneur ; sorties non bufferisées pour
# que `docker logs` voie tout de suite ce que le programme affiche.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
# Un utilisateur dédié : si le programme est compromis, l'attaquant n'est pas root.
RUN useradd --create-home --uid 1000 app
COPY --from=build /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl
USER app
ENTRYPOINT ["outils"]
CMD ["--help"]
