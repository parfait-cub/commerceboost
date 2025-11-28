import schedule
import time
import threading
import requests
from datetime import datetime, timedelta
from utils.config import Config

class SchedulerService:
    def __init__(self):
        self.base_url = f"http://localhost:{Config.PORT}" if not Config.RENDER else "https://your-app.onrender.com"
    
    def start_scheduler(self):
        """Démarre le planificateur de tâches"""
        # Conseil quotidien à 8h00
        schedule.every().day.at("08:00").do(self.send_daily_tips_job)
        
        # Vérification des essais expirés à 9h00
        schedule.every().day.at("09:00").do(self.check_expired_trials_job)
        
        # Rappels d'essai à 10h00 (NOUVEAU)
        schedule.every().day.at("10:00").do(self.check_trial_reminders_job)
        
        # Health check toutes les 10 minutes (pour Render)
        if Config.RENDER:
            schedule.every(Config.PING_INTERVAL).minutes.do(self.health_check_job)
        
        print("🔧 Scheduler démarré avec les tâches planifiées")
        
        # Lance le scheduler dans un thread séparé
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def send_daily_tips_job(self):
        """Tâche d'envoi des conseils quotidiens"""
        print(f"📨 Envoi des conseils quotidiens à {datetime.now()}")
        try:
            response = requests.post(f"{self.base_url}/send-daily-tips")
            print(f"✅ Conseils envoyés: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur envoi conseils: {e}")
    
    def check_expired_trials_job(self):
        """Vérifie les essais expirés"""
        print(f"🔍 Vérification des essais expirés à {datetime.now()}")
        from data.database import db
        
        expired_trials = db.users.find({
            "subscription_tier": "trial",
            "trial_ends_at": {"$lt": datetime.now()},
            "status": "active"
        })
        
        for user in expired_trials:
            print(f"⏰ Essai expiré pour {user.get('name', 'N/A')}")
            # Ici vous pouvez ajouter la logique pour notifier l'utilisateur
    
    def check_trial_reminders_job(self):
        """Vérifie les essais à expirer et envoie des rappels"""
        from data.database import db
        from core.bot_messenger import messenger_bot
        
        print(f"🔔 Vérification des rappels d'essai à {datetime.now()}")
        
        # Essais qui expirent dans 3 jours
        three_days_from_now = datetime.now() + timedelta(days=3)
        users_3_days = db.users.find({
            "subscription_tier": "trial",
            "trial_ends_at": {"$lte": three_days_from_now, "$gt": datetime.now()},
            "status": "active",
            "onboarding_step": "completed"
        })
        
        for user in users_3_days:
            try:
                messenger_bot.send_trial_reminder(user["user_id"], 3)
                print(f"📨 Rappel 3 jours envoyé à {user.get('name', 'N/A')}")
            except Exception as e:
                print(f"❌ Erreur rappel 3 jours: {e}")
        
        # Essais qui expirent demain
        tomorrow = datetime.now() + timedelta(days=1)
        users_1_day = db.users.find({
            "subscription_tier": "trial", 
            "trial_ends_at": {"$lte": tomorrow, "$gt": datetime.now()},
            "status": "active",
            "onboarding_step": "completed"
        })
        
        for user in users_1_day:
            try:
                messenger_bot.send_trial_reminder(user["user_id"], 1)
                print(f"📨 Rappel 1 jour envoyé à {user.get('name', 'N/A')}")
            except Exception as e:
                print(f"❌ Erreur rappel 1 jour: {e}")
    
    def health_check_job(self):
        """Health check pour garder Render actif"""
        try:
            requests.get(f"{self.base_url}/health")
            print(f"❤️ Health check OK à {datetime.now()}")
        except Exception as e:
            print(f"❌ Health check échoué: {e}")

# Instance globale
scheduler = SchedulerService()