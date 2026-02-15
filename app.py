from fastapi import FastAPI, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil
import os
import core  # On importe notre logique
import uuid

app = FastAPI()

# Configuration des dossiers
os.makedirs("uploads", exist_ok=True)
templates = Jinja2Templates(directory="templates")


# Route pour afficher la page web
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Route API pour analyser l'image envoyée
@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    # 1. Sauvegarder l'image temporairement
    filename = f"uploads/{uuid.uuid4()}.jpg"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 2. Pipeline de traitement (Appel à core.py)
        img_traitee = core.pre_traitement_image(filename)

        if img_traitee is None:
            return {"error": "Image illisible"}

        date_trouvee = core.extraire_date_ocr(img_traitee)

        if not date_trouvee:
            return {
                "success": False,
                "message": "Aucune date détectée",
                "filename": file.filename
            }

        couleur, message_statut = core.analyser_peremption(date_trouvee)
        conseil_ia = core.consulter_ia(couleur, date_trouvee)

        # 3. Renvoyer le résultat au format JSON
        return {
            "success": True,
            "filename": file.filename,
            "date": date_trouvee,
            "statut": message_statut,
            "couleur": couleur,  # vert, orange, rouge
            "conseil": conseil_ia
        }

    finally:
        # Nettoyage : on supprime l'image après analyse
        if os.path.exists(filename):
            os.remove(filename)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)