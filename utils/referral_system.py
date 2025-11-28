from data.database import db
from utils.config import Config
from datetime import datetime, timedelta
import random
import string

class ReferralSystem:
    def __init__(self):
        self.referral_discount = Config.REFERRAL_DISCOUNT
    
    def generate_referral_code(self, user_id):
        """Génère un code de parrainage unique"""
        code = f"BOOST{user_id[-4:]}{random.randint(100, 999)}"
        return code.upper()
    
    def create_referral_for_user(self, user_id):
        """Crée un code de parrainage pour un utilisateur"""
        referral_code = self.generate_referral_code(user_id)
        
        db.users.update_one(
            {"user_id": user_id},
            {"$set": {"referral_code": referral_code}}
        )
        
        return referral_code
    
    def apply_referral(self, referred_user_id, referral_code):
        """Applique un parrainage"""
        # Trouve le parrain
        referrer = db.users.find_one({"referral_code": referral_code})
        if not referrer:
            return {"success": False, "error": "Code de parrainage invalide"}
        
        referred_user = db.users.find_one({"user_id": referred_user_id})
        if not referred_user:
            return {"success": False, "error": "Utilisateur non trouvé"}
        
        # Vérifie que l'utilisateur ne se parraine pas lui-même
        if referred_user_id == referrer["user_id"]:
            return {"success": False, "error": "Vous ne pouvez pas vous parrainer vous-même"}
        
        # Vérifie si le parrainage n'existe pas déjà
        existing_referral = db.referrals.find_one({
            "referrer_id": referrer["user_id"],
            "referred_id": referred_user_id
        })
        
        if existing_referral:
            return {"success": False, "error": "Parrainage déjà utilisé"}
        
        # Crée le parrainage
        referral_data = {
            "referrer_id": referrer["user_id"],
            "referred_id": referred_user_id,
            "referral_code": referral_code,
            "referral_date": datetime.now(),
            "status": "pending",  # Devient 'completed' après premier paiement
            "reward_type": "discount",
            "reward_value": self.referral_discount
        }
        
        db.referrals.insert_one(referral_data)
        
        return {
            "success": True,
            "referrer_name": referrer.get("name", "Un commerçant"),
            "discount_percent": int(self.referral_discount * 100)
        }
    
    def get_user_referrals(self, user_id):
        """Récupère les parrainages d'un utilisateur"""
        return list(db.referrals.find({
            "referrer_id": user_id
        }))
    
    def calculate_final_price(self, user_id, base_price):
        """Calcule le prix final avec toutes les réductions applicables"""
        discounts = self.get_applicable_discounts(user_id)
        final_price = base_price
        
        for discount in discounts:
            final_price *= (1 - discount["value"])
        
        return max(final_price, base_price * (1 - Config.MAX_DISCOUNT))
    
    def get_applicable_discounts(self, user_id):
        """Récupère toutes les réductions applicables"""
        discounts = []
        
        # Réduction de parrainage
        referral = db.referrals.find_one({"referred_id": user_id, "status": "pending"})
        if referral:
            discounts.append({
                "type": "referral",
                "value": referral["reward_value"],
                "description": f"Parrainage ({int(referral['reward_value'] * 100)}%)"
            })
        
        # Réduction de bienvenue (premier achat)
        user = db.users.find_one({"user_id": user_id})
        if user and not user.get("used_welcome_discount", False):
            discounts.append({
                "type": "welcome",
                "value": Config.WELCOME_DISCOUNT,
                "description": f"Bienvenue ({int(Config.WELCOME_DISCOUNT * 100)}%)"
            })
        
        return discounts

# Instance globale
referral_system = ReferralSystem()