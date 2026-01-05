# python/services/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import requests
import os
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

scheduler = BackgroundScheduler()

# Keep-alive toutes les 10 minutes
@scheduler.scheduled_job('interval', minutes=10)
def keep_alive():
    try:
        url = os.getenv('RENDER_EXTERNAL_URL') or "https://commerceboost-python.onrender.com/health"
        requests.get(url, timeout=10)
        logging.info("Keep-alive ping envoyé")
    except Exception as e:
        logging.error(f"Keep-alive échoué : {e}")

# Conseil quotidien à 08h00
@scheduler.scheduled_job('cron', hour=8, minute=0)
def send_daily_conseil():
    try:
        response = requests.get("https://commerceboost-python.onrender.com/api/conseil-quotidien")
        if response.status_code == 200:
            conseil = response.json().get('conseil')
            logging.info(f"Conseil quotidien généré : {conseil}")
        else:
            logging.error("Erreur récupération conseil")
    except Exception as e:
        logging.error(f"Erreur conseil quotidien : {e}")

scheduler.start()
logging.info("Scheduler démarré – keep-alive + conseil quotidien")

while True:
    time.sleep(60)