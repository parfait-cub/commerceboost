# python/content_api.py
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from content_manager import calculer_marge, generer_conseil_quotidien, generer_promo
from pymongo import MongoClient
from utils.config import Config
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["200/day", "50/minute"])

client = MongoClient(Config.MONGODB_URI)
db = client['commerceboost']
users_col = db['users']
feedback_col = db['feedback']

logging.basicConfig(level=logging.INFO)

@app.route('/api/calcul-prix', methods=['POST'])
def calcul_prix():
    data = request.get_json()
    achat = data.get('achat', 0)
    frais = data.get('frais', 0)
    vente = data.get('vente', 0)
    result = calculer_marge(achat, frais, vente)
    return jsonify(result)

@app.route('/api/conseil-quotidien', methods=['GET'])
def conseil_quotidien():
    return jsonify({"conseil": generer_conseil_quotidien()})

@app.route('/api/promo', methods=['POST'])
def promo():
    data = request.get_json()
    type_promo = data.get('type', 'jour')
    return jsonify({"message": generer_promo(type_promo)})

@app.route('/api/profile', methods=['POST'])
def save_profile():
    data = request.get_json()
    user_id = data['user_id']
    profile = {
        "niveau_prix": data['niveau_prix'],
        "objectif": data['objectif'],
        "subscription": {"active": True, "type": "trial", "expiry": datetime.now() + timedelta(days=7)},
        "created_at": datetime.now()
    }
    users_col.update_one({"user_id": user_id}, {"$set": profile}, upsert=True)
    return jsonify({"success": True})

@app.route('/api/sub-check', methods=['GET'])
def sub_check():
    user_id = request.args.get('user_id')
    user = users_col.find_one({"user_id": user_id})
    if not user or not user.get('subscription', {}).get('active'):
        return jsonify({"active": False})
    expiry = user['subscription'].get('expiry')
    if expiry and datetime.now() > expiry:
        users_col.update_one({"user_id": user_id}, {"$set": {"subscription.active": False}})
        return jsonify({"active": False})
    return jsonify({"active": True})

@app.route('/api/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    feedback_col.insert_one({
        "user_id": data['user_id'],
        "reaction": data['reaction'],
        "timestamp": datetime.now()
    })
    return jsonify({"success": True})

# V2 commentée – à activer plus tard
# from google.generativeai import GenerativeModel
# model = GenerativeModel('gemini-1.5-flash')
# def analyser_capture(image_url):
#     # Analyse image Flooz/TMoney → extrait montant/numéro/date
#     # Retourne dict ou erreur
#     pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)