# syntax=docker/dockerfile:1

# --- Étape 1 : construire les wheels (outils de build absents de l'image finale) ---
FROM python:3.12-slim AS build
WORKDIR /build
COPY pyproject.toml ./
COPY src ./src
RUN pip wheel --no-cache-dir --wheel-dir /wheels .

# --- Étape 2 (optionnelle) : lint + tests, utilisée par bin/test ---
FROM build AS test
RUN pip install --no-cache-dir -e ".[dev]"
COPY tests ./tests
COPY sources.csv ./
CMD ["sh", "-c", "ruff check . && ruff format --check . && pytest -q"]

# --- Étape finale : image d'exécution, petite et non root ---
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd --create-home --uid 10001 gazette
WORKDIR /app
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels \
    && mkdir -p /app/data && chown gazette:gazette /app/data
COPY sources.csv ./
USER gazette
ENTRYPOINT ["python", "-m", "gazette.collect"]
CMD ["--out-dir", "/app/data/raw"]
