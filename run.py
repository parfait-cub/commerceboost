from app import app
from services.scheduler import scheduler
from data.content_manager import content_manager
from core.bot_telegram import telegram_bot
import threading

def initialize_app():
    """Initialise l'application"""
    print("🚀 Initialisation de CommerceBoost...")
    
    # Initialise le contenu
    content_manager._initialize_content()
    print("✅ Contenu pré-défini initialisé")
    
    # Démarre le scheduler
    scheduler.start_scheduler()
    print("✅ Scheduler démarré")
    
    # Démarre le bot Telegram dans un thread séparé
    def start_telegram_bot():
        try:
            telegram_bot.start_bot()
        except Exception as e:
            print(f"❌ Erreur bot Telegram: {e}")
    
    if telegram_bot.token:
        telegram_thread = threading.Thread(target=start_telegram_bot, daemon=True)
        telegram_thread.start()
        print("✅ Bot Telegram démarré")
    else:
        print("⚠️ Bot Telegram non configuré (TELEGRAM_BOT_TOKEN manquant)")
    
    print(f"🎯 CommerceBoost prêt sur le port {app.config.get('PORT', 10001)}")

if __name__ == '__main__':
    initialize_app()
    app.run(host='0.0.0.0', port=10001, debug=False)