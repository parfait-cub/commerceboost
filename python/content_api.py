from flask import Flask, request, jsonify
import logging
import os
from functools import wraps
from pymongo import MongoClient
from content_manager import (
    calcul_marge,
    conseil_aleatoire,
    generer_promo,
    ajouter_conseil,
    ajouter_promo
)

# Logging SAFE (aucun champ dynamique)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)

API_TOKEN = os.getenv("API_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")

# Mongo best-effort
try:
    mongo = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
    db = mongo["commerceboost"]
    users = db["users"]
except Exception as e:
    logging.error(f"Mongo init error: {e}")
    users = None


def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if token != API_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/prix", methods=["POST"])
@auth_required
def prix():
    data = request.json or {}
    result = calcul_marge(
        data.get("prix_achat", 0),
        data.get("charges", 0),
        data.get("prix_vente", 0)
    )
    if not result:
        return jsonify({"error": "Invalid input"}), 400
    result["conseil"] = conseil_aleatoire()
    return jsonify(result)


@app.route("/promo", methods=["POST"])
@auth_required
def promo():
    data = request.json or {}
    message = generer_promo(data.get("type", "general"))
    return jsonify({"message": message})


@app.route("/admin/conseil", methods=["POST"])
@auth_required
def admin_conseil():
    conseil = request.json.get("conseil")
    if not conseil:
        return jsonify({"error": "Missing conseil"}), 400
    ajouter_conseil(conseil)
    return jsonify({"status": "added"})


@app.route("/admin/promo", methods=["POST"])
@auth_required
def admin_promo():
    data = request.json or {}
    ajouter_promo(data.get("type", "general"), data.get("message", ""))
    return jsonify({"status": "added"})
