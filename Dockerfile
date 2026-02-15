# 1. Utiliser une image Python légère
FROM python:3.10-slim

# 2. Définir le dossier de travail
WORKDIR /app

# 3. Installer les dépendances système pour OpenCV (obligatoire)
# Le 'rm -rf' permet de nettoyer le cache pour gagner de la place
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# 4. ASTUCE CRITIQUE : Installer PyTorch version CPU (très léger) AVANT le reste
# Cela évite de télécharger la version GPU qui pèse 2Go
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 5. Installer EasyOCR maintenant (il utilisera le PyTorch CPU déjà installé)
RUN pip install --no-cache-dir easyocr

# 6. Copier et installer le reste des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copier tout le code du projet (en respectant le .dockerignore)
COPY . .

# 8. Créer le dossier uploads pour éviter les erreurs de permission
RUN mkdir -p uploads && chmod 777 uploads

# 9. Lancer l'application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]