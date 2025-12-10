# python/utils/feedback_system.py
from pymongo import MongoClient
from utils.config import Config
from datetime import datetime

client = MongoClient(Config.MONGODB_URI)
db = client['commerceboost']
feedback_col = db['feedback']

def submit_feedback(user_id: str, message: str, rating: int = None):
    if rating and not (1 <= rating <= 5):
        return {"error": "Rating 1-5"}
    feedback = {"user_id": user_id, "message": message, "rating": rating, "timestamp": datetime.now()}
    feedback_col.insert_one(feedback)
    return {"success": True}

def get_user_history(user_id: str):
    return list(feedback_col.find({"user_id": user_id}).sort("timestamp", -1))