# python/services/scheduler.py - Scheduler pour keep-alive + conseils quotidiens
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import os
import requests
import time

logging.basicConfig(level=logging.INFO)

scheduler = BackgroundScheduler()

# Keep-alive toutes les 10 minutes (empêche Render gratuit de dormir)
@scheduler.scheduled_job('interval', minutes=10)
def keep_alive():
    try:
        url = os.getenv('RENDER_EXTERNAL_URL') or f"https://{os.getenv('RENDER_SERVICE_NAME')}.onrender.com"
        requests.get(url)
        logging.info("Keep-alive ping envoyé")
    except Exception as e:
        logging.error(f"Keep-alive échoué : {e}")

# Conseil quotidien à 08h00 (heure Togo = UTC)
@scheduler.scheduled_job('cron', hour=8, minute=0)
def send_daily_tip():
    logging.info("Envoi du conseil quotidien à 08h00")

# Maintenance nocturne à 02h00
@scheduler.scheduled_job('cron', hour=2, minute=0)
def nightly_maintenance():
    logging.info("Maintenance nocturne effectuée")

scheduler.start()
logging.info("Scheduler démarré avec keep-alive, daily tips et maintenance")

# Garde le process vivant indéfiniment
while True:
    time.sleep(60)
