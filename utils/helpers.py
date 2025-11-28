from datetime import datetime, timedelta

def format_date(date_obj):
    """Formate une date en français"""
    return date_obj.strftime("%d/%m/%Y à %H:%M")

def days_until(target_date):
    """Calcule le nombre de jours jusqu'à une date"""
    today = datetime.now().date()
    return (target_date.date() - today).days

def calculate_discount_price(original_price, discount_percent):
    """Calcule le prix après réduction"""
    discount_amount = original_price * discount_percent
    final_price = original_price - discount_amount
    return max(final_price, original_price * 0.5)  # Minimum 50% du prix original

def get_business_type_emoji(business_type):
    """Retourne l'emoji correspondant au type de commerce"""
    emojis = {
        "physique": "🏪",
        "en_ligne": "🌐", 
        "mixte": "📱"
    }
    return emojis.get(business_type, "🏢")

def get_sector_emoji(sector):
    """Retourne l'emoji correspondant au secteur"""
    emojis = {
        "alimentaire": "🍕",
        "mode": "👕",
        "beaute": "💄",
        "electronique": "📱",
        "maison": "🏠",
        "autre": "➕"
    }
    return emojis.get(sector, "📊")