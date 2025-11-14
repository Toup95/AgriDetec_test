# Utiliser Python 3.11 (meilleure compatibilité que 3.13)
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers requirements
COPY requirements.txt .

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier tout le code de l'application
COPY . .

# Exposer le port
EXPOSE 8000

# Variables d'environnement par défaut
ENV AGRIDETECT_MODEL_PATH=./models/agridetect_model_20251107_042206
ENV ENVIRONMENT=production
ENV DEBUG=False

# Commande de démarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]