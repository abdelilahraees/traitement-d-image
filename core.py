import cv2
import easyocr
import re
from datetime import datetime
import google.generativeai as genai
import os
import gc  # Module "Garbage Collector" essentiel pour nettoyer la RAM

# --- CONFIGURATION IA ---
# Votre clé est intégrée ici
API_KEY_GEMINI = "AIzaSyAhbKekkBFPUgDR0pSrM6dogU8ECWEU4Gk"

# On active l'IA automatiquement si la clé semble valide
UTILISER_VRAIE_IA = True if API_KEY_GEMINI and "AIzaSy" in API_KEY_GEMINI else False

if UTILISER_VRAIE_IA:
    try:
        genai.configure(api_key=API_KEY_GEMINI)
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
        print(f"Erreur configuration Gemini: {e}")
        UTILISER_VRAIE_IA = False

# 🛑 ATTENTION : J'ai supprimé la ligne 'reader = ...' qui était ici.
# C'est elle qui faisait planter votre serveur au démarrage !

def pre_traitement_image(image_path):
    img = cv2.imread(image_path)
    if img is None: return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return thresh


def extraire_date_ocr(image_processed):
    try:
        # 🟢 CHARGEMENT À LA DEMANDE (LAZY LOADING)
        # On charge le modèle uniquement au moment précis où on en a besoin
        print("Chargement EasyOCR en mémoire...")
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)

        # Lecture
        resultats = reader.readtext(image_processed, detail=0)
        texte_complet = " ".join(resultats)

        # 🔴 NETTOYAGE IMMÉDIAT (CRITIQUE POUR KOYEB)
        # On supprime le modèle de la RAM tout de suite après pour éviter le crash
        del reader
        gc.collect()  # On force le nettoyage de la RAM
        print("Mémoire libérée.")

        # Correction et Regex
        texte_complet = texte_complet.replace('O', '0').replace('o', '0')
        pattern_date = r"(\d{2})[./\-\s](\d{2})[./\-\s](\d{2,4})"
        matches = re.findall(pattern_date, texte_complet)

        if matches:
            jour, mois, annee = matches[0]
            if len(annee) == 2: annee = "20" + annee
            return f"{jour}/{mois}/{annee}"

    except Exception as e:
        print(f"Erreur OCR: {e}")

    return None


def analyser_peremption(date_str):
    try:
        date_dlc = datetime.strptime(date_str, "%d/%m/%Y")
        aujourd_hui = datetime.now()
        delta = (date_dlc - aujourd_hui).days + 1

        if delta < 0:
            return "rouge", f"PÉRIMÉ depuis {abs(delta)} jours"
        elif 0 <= delta <= 3:
            return "orange", f"Expire dans {delta} jours !"
        else:
            return "vert", f"VALIDE : Encore {delta} jours"
    except:
        return "gris", "Erreur format date"


def consulter_ia(alerte, date):
    if not UTILISER_VRAIE_IA:
        # Mode de secours si l'IA échoue
        if alerte == "orange": return "🤖 IA (Simu) : Faites une quiche ou un gratin !"
        if alerte == "rouge": return "🤖 IA (Simu) : Attention, risque bactérien."
        return "Pas de conseil."

    prompt = ""
    if alerte == "orange":
        prompt = f"Un produit expire le {date}. Donne une idée de recette express anti-gaspillage. Court."
    elif alerte == "rouge":
        prompt = f"Un produit est périmé depuis le {date}. Quels sont les risques sanitaires ? Sois bref."

    if prompt:
        try:
            response = model.generate_content(prompt)
            return f"✨ Gemini : {response.text}"
        except Exception as e:
            return f"Erreur IA : {str(e)}"
    return ""