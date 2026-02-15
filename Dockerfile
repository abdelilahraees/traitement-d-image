# 1. Utiliser une image Python légère
FROM python:3.10-slim

# 2. Définir le dossier de travail
WORKDIR /app

# 3. Installer les dépendances système pour OpenCV
# On utilise libgl1 au lieu de libgl1-mesa-glx pour éviter l'erreur Debian
RUN apt-get update && apt-get install -y \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. ASTUCE CRITIQUE : Installer PyTorch CPU (léger) AVANT easyocr
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 5. Installer le reste des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copier le code
COPY . .

# 7. Permissions uploads
RUN mkdir -p uploads && chmod 777 uploads

# 8. Lancer
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]