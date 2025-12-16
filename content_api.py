# python/content_api.py
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pydantic import BaseModel, ValidationError
from content_manager import expert_ai
from utils.beta_manager import register_beta
from utils.referral_system import apply_referral, generate_referral_code
from utils.feedback_system import submit_feedback, get_user_history
from pymongo import MongoClient
from utils.config import Config
import logging

app = Flask(__name__)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["200/day", "60/minute"])

client = MongoClient(Config.MONGODB_URI)
db = client['commerceboost']
users_col = db['users']

class IARequest(BaseModel):
    user_id: str
    question: str
    context: dict = {}

class ProfileRequest(BaseModel):
    user_id: str
    profile: dict

class BetaRequest(BaseModel):
    user_id: str
    code: str

class ReferralApplyRequest(BaseModel):
    code: str
    new_user_id: str

class ReferralGenerateRequest(BaseModel):
    user_id: str

logging.basicConfig(level=logging.INFO, filename='api.log', filemode='a')

@app.before_request
def check_auth():
    auth = request.headers.get('Authorization')
    if auth != f"Bearer {Config.API_TOKEN}":
        return jsonify({"error": "Non autorisé"}), 401

@app.route('/api/ia', methods=['POST'])
def ia_endpoint():
    data = request.get_json()
    question = data.get('question', '').strip()
    user_context = data.get('context', {})

    if not question:
        return jsonify({"error": "Question vide"}), 400

    response = expert_ai.generate_response(question, user_context)
    return jsonify({"response": response})

@app.route('/api/user/profile', methods=['POST'])
def update_profile():
    try:
        data = ProfileRequest(**request.json)
        existing = users_col.find_one({"user_id": data.user_id})
        if not existing:
            is_beta = 'beta_code' in data.profile  # Simplifié
            trial_days = 21 if is_beta else 5
            trial_end = datetime.now() + timedelta(days=trial_days)
            data.profile.update({
                'is_beta': is_beta,
                'subscription': {'type': 'trial', 'active': True, 'expiry': trial_end},
                'created_at': datetime.now()
            })
        users_col.update_one({"user_id": data.user_id}, {"$set": data.profile}, upsert=True)
        return jsonify({"success": True})
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/beta/register', methods=['POST'])
def beta_register():
    try:
        data = BetaRequest(**request.json)
        return jsonify(register_beta(data.user_id, data.code))
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/referral/generate', methods=['POST'])
def referral_generate():
    try:
        data = ReferralGenerateRequest(**request.json)
        code = generate_referral_code(data.user_id)
        return jsonify({"code": code})
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/referral/apply', methods=['POST'])
def referral_apply():
    try:
        data = ReferralApplyRequest(**request.json)
        return jsonify(apply_referral(data.code, data.new_user_id))
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/subscription/check', methods=['GET'])
def check_sub():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id requis"}), 400
    user = users_col.find_one({"user_id": user_id})
    if not user:
        return jsonify({"active": False})
    sub = user.get('subscription', {})
    if sub.get('type') == 'beta':
        return jsonify({"active": True, "type": "beta"})
    if 'expiry' in sub and datetime.now() > sub['expiry']:
        sub['active'] = False
        users_col.update_one({"user_id": user_id}, {"$set": {"subscription": sub}})
    return jsonify({"active": sub.get('active', False), "type": sub.get('type')})

@app.route('/api/admin/users', methods=['GET'])
def admin_users():
    users = list(users_col.find({}, {"_id": 0, "user_id": 1, "business_type": 1, "subscription": 1}))
    return jsonify(users)

# Ajoute /api/feedback/submit etc. si besoin

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)