# AgenticAI V4 - Backend Dockerfile
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="AgenticAI Team"
LABEL version="4.0.0"
LABEL description="AgenticAI V4 Backend - Multi-Agent Assistant"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Créer un utilisateur non-root
RUN useradd -m -u 1000 agenticai && \
    mkdir -p /app /app/logs && \
    chown -R agenticai:agenticai /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY --chown=agenticai:agenticai pyproject.toml requirements-dev.txt ./

# Installer les dépendances Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e .

# Copier le code source
COPY --chown=agenticai:agenticai . .

# Basculer vers l'utilisateur non-root
USER agenticai

# Exposer le port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande par défaut
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
