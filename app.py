from flask import Flask, request, jsonify
from utils.config import Config
from core.bot_messenger import messenger_bot
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Vérification webhook Facebook
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if verify_token == Config.FACEBOOK_VERIFY_TOKEN:
            return challenge
        else:
            return 'Token de vérification invalide', 403
    
    else:
        # Gestion des messages entrants
        return messenger_bot.handle_message(request.get_json())

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "commerceboost",
        "version": "1.0"
    })

@app.route('/send-daily-tips', methods=['POST'])
def send_daily_tips():
    """Endpoint pour envoyer les conseils quotidiens (appelé par le scheduler)"""
    from data.database import db
    
    # Récupère tous les utilisateurs actifs avec onboarding complet
    active_users = db.users.find({
        "status": "active", 
        "onboarding_step": "completed"
    })
    
    results = []
    for user in active_users:
        try:
            messenger_bot.send_daily_tip(user["user_id"])
            results.append({"user_id": user["user_id"], "status": "sent"})
        except Exception as e:
            results.append({"user_id": user["user_id"], "status": "error", "error": str(e)})
    
    return jsonify({
        "sent_at": datetime.now().isoformat(),
        "results": results
    })

@app.route('/cron/daily-tips', methods=['POST'])
def cron_daily_tips():
    """Endpoint pour cron externe"""
    auth_token = request.headers.get('Authorization')
    if auth_token != f"Bearer {Config.ADMIN_KEY}":
        return jsonify({"error": "Unauthorized"}), 401
    
    from data.database import db
    
    active_users = db.users.find({
        "status": "active",
        "onboarding_step": "completed"
    })
    results = []
    
    for user in active_users:
        try:
            messenger_bot.send_daily_tip(user["user_id"])
            results.append({"user_id": user["user_id"], "status": "sent"})
        except Exception as e:
            results.append({"user_id": user["user_id"], "status": "error", "error": str(e)})
    
    return jsonify({
        "sent_at": datetime.now().isoformat(),
        "total_sent": len([r for r in results if r["status"] == "sent"]),
        "errors": len([r for r in results if r["status"] == "error"])
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', Config.PORT))
    app.run(host='0.0.0.0', port=port, debug=(Config.NODE_ENV == 'development'))