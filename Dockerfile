# Utilisation de l'image Python officielle
FROM python:3.12-slim

# Installation des dépendances système nécessaires pour Chrome et Chromedriver
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxrandr2 \
    libxtst6 \
    fonts-liberation \
    xdg-utils \
    libu2f-udev \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Téléchargement et installation de Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Création d'un dossier pour l'application
WORKDIR /app

# Copie des fichiers du projet
COPY . /app

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port de l'application
EXPOSE 8000

# Lancer l'application FastAPI avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

