# 1. Utiliser une image Python légère
FROM python:3.10-slim

# 2. Définir le dossier de travail
WORKDIR /app

# 3. Installer les dépendances système pour OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Installer PyTorch CPU (léger)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 5. Installer EasyOCR et les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- ASTUCE MAGIQUE ICI ---
# 6. On force le téléchargement des modèles EasyOCR MAINTENANT (pendant le build)
# Comme ça, ils seront déjà dans l'image et on n'aura pas à le faire au démarrage.
# Cela évite le pic de RAM qui fait planter votre serveur.
RUN python -c "import easyocr; print('Téléchargement des modèles...'); easyocr.Reader(['en'], gpu=False)"

# 7. Copier le reste du code
COPY . .

# 8. Permissions uploads
RUN mkdir -p uploads && chmod 777 uploads

# 9. Lancer
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]