import hashlib
import hmac
from utils.config import Config

def verify_signature(payload, signature):
    """Vérifie la signature des webhooks"""
    expected_signature = hmac.new(
        Config.JWT_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

def generate_referral_code(user_id):
    """Génère un code de parrainage unique"""
    return f"BOOST-{user_id[:6].upper()}"

def validate_phone_number(phone):
    """Valide un numéro de téléphone Togo"""
    # Format attendu: 228XXXXXXXX
    if phone.startswith('+228'):
        phone = phone[1:]  # Enlève le +
    elif phone.startswith('00228'):
        phone = phone[2:]  # Enlève le 00
    
    return phone.startswith('228') and len(phone) == 11 and phone[3:].isdigit()