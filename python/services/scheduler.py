# python/services/scheduler.py (modifié)
import sys
sys.path.append('/opt/render/project/src')  # Ajoute la racine pour trouver utils/
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pymongo import MongoClient
from utils.config import Config
from datetime import datetime, timedelta
import logging
import requests
import random

logging.basicConfig(level=logging.INFO)

client = MongoClient(Config.MONGODB_URI)
db = client['commerceboost']
users_col = db['users']
tips_col = db['daily_tips']  # Nouvelle collection

scheduler = BackgroundScheduler()

# Envoi conseils quotidiens à 08h : Fetch de DB (aléatoire non récent)
@scheduler.scheduled_job(CronTrigger(hour=8, minute=0))
def send_daily_tips():
    # Trouve un tip non envoyé depuis 180+ jours (ou random si tous récents)
    recent_threshold = datetime.now() - timedelta(days=180)
    tip = tips_col.find_one({"last_sent": {"$lt": recent_threshold}})
    if not tip:
        tip = tips_col.aggregate([{ "$sample": { "size": 1 } }]).next()  # Fallback random

    content = tip['content']

    users = users_col.find({"subscription.active": True})
    for user in users:
        # Personnalise légèrement si besoin (ex: ajouter nom)
        message = f"Conseil quotidien CommerceBoost :\n{content}"
        # Envoi via webhook bots (adapte à tes webhooks existants)
        requests.post("https://ton-bot-webhook/notify", json={"user_id": user['user_id'], "message": message})

    # Update last_sent
    tips_col.update_one({"_id": tip['_id']}, {"$set": {"last_sent": datetime.now()}})
    logging.info("Tip envoyé : ID " + str(tip['id']))

# ... (autres jobs inchangés : maintenance, notifs expirations)

if __name__ == '__main__':
    scheduler.start()
    input("Presse Enter pour arrêter...")