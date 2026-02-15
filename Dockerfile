# 1. Utiliser une image Python légère
FROM python:3.10-slim

# 2. Définir le dossier de travail
WORKDIR /app

# 3. Installer les dépendances système (OpenCV)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Installer PyTorch CPU (Léger)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 5. Installer EasyOCR et les autres librairies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- 🚀 L'ASTUCE QUI SAUVE LA MÉMOIRE ---
# 6. On télécharge les modèles EasyOCR MAINTENANT (pendant le Build)
# Comme ça, ils sont gravés dans l'image. Plus de téléchargement au démarrage !
RUN python -c "import easyocr; print('Pré-téléchargement des modèles...'); easyocr.Reader(['en'], gpu=False)"

# 7. Copier le reste du code
COPY . .

# 8. Permissions pour les uploads
RUN mkdir -p uploads && chmod 777 uploads

# 9. Lancer l'application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]