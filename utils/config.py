import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Core
    NODE_ENV = os.getenv('NODE_ENV', 'production')
    PORT = int(os.getenv('PORT', 10001))
    
    # Security
    VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
    ADMIN_KEY = os.getenv('ADMIN_KEY')
    JWT_SECRET = os.getenv('JWT_SECRET')
    
    # Database
    MONGODB_URI = os.getenv('MONGODB_URI')
    
    # AI
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-lite')
    
    # Facebook
    FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
    FACEBOOK_VERIFY_TOKEN = os.getenv('FACEBOOK_VERIFY_TOKEN')
    
    # Business
    TRIAL_DAYS = int(os.getenv('TRIAL_DAYS', 7))
    DEMARRAGE_PRICE = int(os.getenv('DEMARRAGE_PRICE', 3000))
    CROISSANCE_PRICE = int(os.getenv('CROISSANCE_PRICE', 5000))
    ELITE_PRICE = int(os.getenv('ELITE_PRICE', 10000))
    
    # Optimization
    RENDER = os.getenv('RENDER', 'false').lower() == 'true'
    PING_INTERVAL = int(os.getenv('PING_INTERVAL', 10))
    
    # Promotions
    REFERRAL_DISCOUNT = float(os.getenv('REFERRAL_DISCOUNT', 0.10))
    WELCOME_DISCOUNT = float(os.getenv('WELCOME_DISCOUNT', 0.20))
    MAX_DISCOUNT = float(os.getenv('MAX_DISCOUNT', 0.50))
    
    # Telegram Admin
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    ADMIN_USER_IDS = [int(id.strip()) for id in os.getenv('ADMIN_USER_IDS', '').split(',') if id.strip()]