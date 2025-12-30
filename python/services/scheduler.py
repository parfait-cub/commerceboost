# python/services/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import requests
import os
import time

logging.basicConfig(level=logging.INFO)

scheduler = BackgroundScheduler()

# Keep-alive toutes les 10 min
@scheduler.scheduled_job('interval', minutes=10)
def keep_alive():
    try:
        requests.get(os.getenv('RENDER_EXTERNAL_URL', 'https://commerceboost-python.onrender.com/health'))
    except:
        pass

# Conseil quotidien à 08h
@scheduler.scheduled_job('cron', hour=8, minute=0)
def send_daily_conseil():
    try:
        response = requests.get('https://commerceboost-python.onrender.com/api/conseil-quotidien')
        conseil = response.json().get('conseil', 'Bonne journée !')
        # Ici tu peux ajouter l’envoi aux users via webhook Node plus tard
        logging.info(f"Conseil envoyé : {conseil}")
    except Exception as e:
        logging.error(f"Erreur conseil : {e}")

scheduler.start()
logging.info("Scheduler démarré")

while True:
    time.sleep(60)