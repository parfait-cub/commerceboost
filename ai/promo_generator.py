from data.database import db
from data.content_manager import content_manager
import random
from datetime import datetime

class PromoGenerator:
    def __init__(self):
        self.promo_types = {
            "stock_lent": "Pour écouler un stock lent",
            "nouveaux_clients": "Pour attirer de nouveaux clients",
            "fidelisation": "Pour fidéliser les clients existants", 
            "lancement": "Pour lancer un nouveau produit"
        }
    
    def generate_promotion(self, user_id, promo_type, sector, business_type):
        """Génère une promotion personnalisée selon le type de commerce"""
        # Essaie d'abord les promotions pré-définies adaptées
        predefined_promos = content_manager.get_predefined_promos(promo_type, sector, business_type)
        
        if predefined_promos:
            promo = random.choice(predefined_promos)
        else:
            # Fallback sur des templates génériques adaptés
            promo = self._generate_fallback_promo(promo_type, business_type)
        
        # Sauvegarde la promotion générée
        promo_data = {
            "user_id": user_id,
            "promo_type": promo_type,
            "sector": sector,
            "business_type": business_type,
            "titre": promo["titre"],
            "description": promo["description"],
            "avantage": promo.get("avantage", ""),
            "exemple": promo.get("exemple", ""),
            "generated_date": datetime.now(),
            "status": "suggested"
        }
        
        db.promotions.insert_one(promo_data)
        
        return promo_data
    
    def _generate_fallback_promo(self, promo_type, business_type):
        """Génère une promotion de secours adaptée au type de commerce"""
        templates_physique = {
            "stock_lent": {
                "titre": "Coin Soldes Physique",
                "description": "Espace dédié aux articles en promotion dans votre boutique",
                "avantage": "Attire les chasseurs de bonnes affaires en magasin",
                "exemple": "Zone bien visible avec signalétique '-50%'"
            },
            "nouveaux_clients": {
                "titre": "Cadeau de Bienvenue",
                "description": "Offre spéciale pour les nouveaux clients en boutique",
                "avantage": "Convertit les nouveaux visiteurs en clients fidèles",
                "exemple": "Petit cadeau ou réduction sur le premier achat"
            }
        }
        
        templates_en_ligne = {
            "stock_lent": {
                "titre": "Flash Sale Digital",
                "description": "Promotion limitée dans le temps sur vos réseaux",
                "avantage": "Crée de l'urgence et booste l'engagement",
                "exemple": "Vente flash de 4 heures sur WhatsApp/Facebook"
            },
            "nouveaux_clients": {
                "titre": "Code Bienvenue Online",
                "description": "Code promo pour première commande en ligne",
                "avantage": "Incite à la première commande digitale",
                "exemple": "Code BIENVENUE10 pour -10% sur la première commande"
            }
        }
        
        templates_mixte = {
            "stock_lent": {
                "titre": "Soldes Multi-Canal",
                "description": "Promotion disponible en boutique et en ligne",
                "avantage": "Maximise la visibilité et les ventes",
                "exemple": "Même promotion annoncée partout pour cohérence"
            },
            "fidelisation": {
                "titre": "Fidélité Cross-Canal",
                "description": "Programme de fidélité valable partout",
                "avantage": "Fidélise les clients sur tous les canaux",
                "exemple": "Points cumulables en ligne et en boutique"
            }
        }
        
        # Sélectionne le template adapté
        if business_type == "physique":
            templates = templates_physique
        elif business_type == "en_ligne":
            templates = templates_en_ligne
        else:
            templates = templates_mixte
        
        return templates.get(promo_type, {
            "titre": "Offre Spéciale",
            "description": "Promotion adaptée à votre type de commerce",
            "avantage": "Boostez vos ventes efficacement",
            "exemple": "Personnalisez cette offre selon vos besoins"
        })
    
    def get_user_promotions(self, user_id, limit=5):
        """Retourne l'historique des promotions d'un utilisateur"""
        return list(db.promotions.find(
            {"user_id": user_id}
        ).sort("generated_date", -1).limit(limit))

# Instance globale
promo_generator = PromoGenerator()