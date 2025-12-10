# python/utils/referral_system.py
from pymongo import MongoClient
from utils.config import Config
import uuid
from datetime import datetime

client = MongoClient(Config.MONGODB_URI)
db = client['commerceboost']
users_col = db['users']
referrals_col = db['referrals']
users_col.create_index("referral_code", unique=True)

def generate_referral_code(user_id: str):
    code = uuid.uuid4().hex[:6].upper()
    users_col.update_one({"user_id": user_id}, {"$set": {"referral_code": code}})
    return code

def apply_referral(referrer_code: str, new_user_id: str):
    referrer = users_col.find_one({"referral_code": referrer_code})
    if not referrer:
        return {"error": "Code invalide"}
    discount = 0.3
    users_col.update_one({"user_id": new_user_id}, {"$set": {"referrer_id": referrer['user_id'], "discount": discount}})
    users_col.update_one({"user_id": referrer['user_id']}, {"$inc": {"referral_count": 1}, "$set": {"discount": discount}})
    referrals_col.insert_one({"referrer_id": referrer['user_id'], "referred_id": new_user_id, "timestamp": datetime.now()})
    # Notif via bot webhook si besoin
    return {"success": True}