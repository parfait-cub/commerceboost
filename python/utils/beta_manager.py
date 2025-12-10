# python/utils/beta_manager.py
from pymongo import MongoClient
from utils.config import Config
import uuid
from datetime import datetime, timedelta

client = MongoClient(Config.MONGODB_URI)
db = client['commerceboost']
users_col = db['users']
users_col.create_index("user_id", unique=True)
users_col.create_index("beta_code", unique=True)

BETA_LIMIT = 50
GROUP_LINK = Config.WHATSAPP_GROUP_LINK

def generate_beta_code():
    return uuid.uuid4().hex[:8].upper()

def is_beta_available():
    return users_col.count_documents({"is_beta": True}) < BETA_LIMIT

def register_beta(user_id: str, code: str):
    if users_col.find_one({"beta_code": code}):
        return {"error": "Code déjà utilisé"}
    if not is_beta_available():
        return {"error": "Programme bêta plein"}
    update = {
        "$set": {
            "is_beta": True,
            "beta_code": code,
            "subscription": {"type": "beta", "price": 8000, "active": True, "expiry": None},
            "trial_end": datetime.now() + timedelta(weeks=3)
        }
    }
    users_col.update_one({"user_id": user_id}, update, upsert=True)
    return {"success": True, "group_link": GROUP_LINK}