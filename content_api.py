# content_api.py
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from content_manager import calculer_marge, generer_conseil_quotidien, generer_promo
from pymongo import MongoClient
from utils.config import Config
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per minute"])

client = MongoClient(Config.MONGODB_URI)
db = client['commerceboost']
users_col = db['users']
feedback_col = db['feedback']
user_states_col = db['user_states']  # État utilisateur en DB

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - user:%(user_id)s - %(message)s')

@app.before_request
def check_auth():
    if request.path in ['/health']:
        return
    auth = request.headers.get('Authorization')
    if auth != f"Bearer {Config.API_TOKEN}":
        logging.warning("Accès non autorisé depuis %s", request.remote_addr)
        return jsonify({"error": "Non autorisé"}), 401

@app.route('/health')
def health():
    return jsonify({"status": "OK", "time": datetime.now().isoformat()})

@app.route('/api/calcul-prix', methods=['POST'])
@limiter.limit("20 per minute")
def calcul_prix():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    achat = data.get('achat', 0)
    frais = data.get('frais', 0)
    vente_actuel = data.get('vente_actuel', 0)

    if not all(isinstance(x, (int, float)) for x in [achat, frais, vente_actuel]):
        return jsonify({"error": "Valeurs numériques requises"}), 400
    if achat <= 0 or frais < 0 or vente_actuel <= 0:
        return jsonify({"error": "Valeurs positives requises"}), 400
    if achat > 1000000 or vente_actuel > 1000000:
        return jsonify({"error": "Valeurs trop élevées"}), 400

    logging.info("Calcul marge", extra={"user_id": user_id})
    result = calculer_marge(achat, frais, vente_actuel)
    return jsonify(result)

@app.route('/api/conseil-quotidien', methods=['GET'])
def conseil_quotidien():
    conseil = generer_conseil_quotidien()
    logging.info("Conseil quotidien généré")
    return jsonify({"conseil": conseil})

@app.route('/api/promo', methods=['POST'])
def promo():
    data = request.get_json() or {}
    type_promo = data.get('type', 'jour')
    message = generer_promo(type_promo)
    return jsonify({"message": message})

@app.route('/api/profile', methods=['POST'])
def save_profile():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    niveau_prix = data.get('niveau_prix')
    objectif = data.get('objectif')

    if niveau_prix not in ['bas', 'moyen', 'élevé']:
        return jsonify({"error": "Niveau prix invalide"}), 400
    if objectif not in ['mieux fixer prix', 'attirer plus de clients']:
        return jsonify({"error": "Objectif invalide"}), 400

    profile = {
        "niveau_prix": niveau_prix,
        "objectif": objectif,
        "subscription": {"active": True, "type": "trial", "expiry": datetime.now() + timedelta(days=7)},
        "created_at": datetime.now()
    }
    users_col.update_one({"user_id": user_id}, {"$set": profile}, upsert=True)
    logging.info("Profil sauvegardé", extra={"user_id": user_id})
    return jsonify({"success": True})

@app.route('/api/sub-check', methods=['GET'])
def sub_check():
    user_id = request.args.get('user_id')
    user = users_col.find_one({"user_id": user_id})
    if not user:
        return jsonify({"active": False})
    sub = user.get('subscription', {})
    active = sub.get('active', False)
    expiry = sub.get('expiry')
    if expiry and datetime.now() > expiry:
        active = False
        users_col.update_one({"user_id": user_id}, {"$set": {"subscription.active": False}})
    return jsonify({"active": active})

@app.route('/api/feedback', methods=['POST'])
def feedback():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    reaction = data.get('reaction')
    if reaction not in ['utile', 'moyen', 'inutile']:
        return jsonify({"error": "Feedback invalide"}), 400
    feedback_col.insert_one({
        "user_id": user_id,
        "reaction": reaction,
        "timestamp": datetime.now()
    })
    logging.info(f"Feedback {reaction}", extra={"user_id": user_id})
    return jsonify({"success": True})

# V2 commentée – Gemini Vision pour paiement manuel semi-auto
# from google.generativeai import GenerativeModel
# model = GenerativeModel('gemini-1.5-flash')
# def analyser_capture(image_url):
#     # À activer en V2 : extraire montant, numéro, date
#     pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))