import cv2
import easyocr
import re
from datetime import datetime
import google.generativeai as genai

# --- CONFIGURATION IA ---
# Remplacez par votre VRAIE clé si vous voulez tester l'IA
API_KEY_GEMINI = "VOTRE_CLE_GEMINI_ICI"
UTILISER_VRAIE_IA = False  # Mettre à True pour activer Gemini

if UTILISER_VRAIE_IA:
    try:
        genai.configure(api_key=API_KEY_GEMINI)
        model = genai.GenerativeModel('gemini-pro')
    except:
        UTILISER_VRAIE_IA = False

# Initialisation OCR (une seule fois au chargement)
print("⏳ Chargement du modèle OCR...")
reader = easyocr.Reader(['en'], gpu=False)


def pre_traitement_image(image_path):
    img = cv2.imread(image_path)
    if img is None: return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return thresh


def extraire_date_ocr(image_processed):
    # Lecture OCR
    resultats = reader.readtext(image_processed, detail=0)
    texte_complet = " ".join(resultats)
    texte_complet = texte_complet.replace('O', '0').replace('o', '0')

    # Regex
    pattern_date = r"(\d{2})[./\-\s](\d{2})[./\-\s](\d{2,4})"
    matches = re.findall(pattern_date, texte_complet)

    if matches:
        jour, mois, annee = matches[0]
        if len(annee) == 2: annee = "20" + annee
        return f"{jour}/{mois}/{annee}"
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
        # Mock (Simulation)
        if alerte == "orange": return "🤖 IA (Simu) : Faites une quiche ou un gratin ce soir !"
        if alerte == "rouge": return "🤖 IA (Simu) : Risque bactérien élevé. Jetez le produit."
        return "Pas de conseil nécessaire."

    # Vraie IA Gemini
    prompt = ""
    if alerte == "orange":
        prompt = f"Un produit expire le {date}. Donne une idée de recette express anti-gaspillage."
    elif alerte == "rouge":
        prompt = f"Un produit est périmé depuis le {date}. Quels sont les risques ? Sois bref."

    if prompt:
        try:
            response = model.generate_content(prompt)
            return f"✨ Gemini : {response.text}"
        except Exception as e:
            return f"Erreur IA : {str(e)}"

    return ""