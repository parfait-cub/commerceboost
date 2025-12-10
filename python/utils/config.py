# python/utils/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MONGODB_URI = os.getenv("MONGODB_URI")
    API_TOKEN = os.getenv("API_TOKEN")  # Pour auth interne
    WHATSAPP_GROUP_LINK = os.getenv("WHATSAPP_GROUP_LINK")