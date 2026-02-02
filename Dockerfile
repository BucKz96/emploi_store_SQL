FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de configuration
COPY pyproject.toml ./

# Installation des dépendances Python
RUN pip install --no-cache-dir -e ".[dev]"

# Copie du code source
COPY emploi_store/ ./emploi_store/
COPY api/ ./api/
COPY cli.py ./

# Création du dossier data
RUN mkdir -p /app/data

# Variables d'environnement par défaut
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///./data/emploi_store.db

EXPOSE 8000

CMD ["python", "cli.py", "api", "--host", "0.0.0.0", "--port", "8000"]
