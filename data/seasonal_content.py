from datetime import datetime
import random

class SeasonalContent:
    def __init__(self):
        self.monthly_tips = {
            12: [  # Décembre - Période de fêtes
                {
                    "secteur": "physique",
                    "conseil": "Décorer votre boutique aux couleurs de Noël et du Nouvel An. Une vitrine festive attire plus de clients en cette période de fêtes.",
                    "tags": ["saisonnier", "decoration", "fêtes", "physique"],
                    "niveau": "all"
                },
                {
                    "secteur": "en_ligne", 
                    "conseil": "Créez une bannière de fêtes sur votre page et proposez la livraison express pour les cadeaux de dernière minute.",
                    "tags": ["saisonnier", "digital", "fêtes", "en_ligne"],
                    "niveau": "intermediaire"
                },
                {
                    "secteur": "physique",
                    "conseil": "Proposez des emballages cadeaux gratuits pour les achats de fin d'année. Ce petit service fait la différence !",
                    "tags": ["saisonnier", "service", "fêtes", "physique"],
                    "niveau": "debutant"
                },
                {
                    "secteur": "en_ligne",
                    "conseil": "Mettez en avant des 'box cadeaux' avec plusieurs produits. Les clients en ligne aiment les idées toutes faites pour les fêtes.",
                    "tags": ["saisonnier", "packaging", "fêtes", "en_ligne"],
                    "niveau": "intermediaire"
                },
                {
                    "secteur": "mixte",
                    "conseil": "Décembre est idéal pour lancer un calendrier de l'avent avec des promotions quotidiennes. Gardez vos clients engagés !",
                    "tags": ["saisonnier", "promotion", "fêtes", "mixte"],
                    "niveau": "experimente"
                }
            ],
            1: [  # Janvier - Début d'année, soldes
                {
                    "secteur": "physique",
                    "conseil": "Janvier = soldes ! Affichez clairement les pourcentages de réduction en vitrine et formez votre personnel aux offres.",
                    "tags": ["saisonnier", "soldes", "physique"],
                    "niveau": "debutant"
                },
                {
                    "secteur": "en_ligne",
                    "conseil": "Optimisez votre site pour les recherches 'soldes janvier'. C'est le moment où les clients comparent les prix en ligne.",
                    "tags": ["saisonnier", "soldes", "digital", "en_ligne"],
                    "niveau": "intermediaire"
                },
                {
                    "secteur": "mixte",
                    "conseil": "Lancez une offre 'bonne année' avec un petit cadeau pour les premiers achats. Parfait pour fidéliser après les fêtes.",
                    "tags": ["saisonnier", "fidelisation", "mixte"],
                    "niveau": "all"
                },
                {
                    "secteur": "en_ligne",
                    "conseil": "Janvier est le mois des bonnes résolutions. Mettez en avant les produits 'nouveau départ' ou 'bien-être'.",
                    "tags": ["saisonnier", "marketing", "en_ligne"],
                    "niveau": "intermediaire"
                }
            ],
            2: [  # Février - Saint Valentin
                {
                    "secteur": "physique",
                    "conseil": "Créez un coin 'Saint-Valentin' dans votre boutique avec des produits cadeaux bien mis en valeur.",
                    "tags": ["saisonnier", "saint_valentin", "physique"],
                    "niveau": "debutant"
                },
                {
                    "secteur": "en_ligne",
                    "conseil": "Lancez une collection 'cadeaux Saint-Valentin' avec des photos romantiques et des descriptions évocatrices.",
                    "tags": ["saisonnier", "saint_valentin", "digital", "en_ligne"],
                    "niveau": "intermediaire"
                },
                {
                    "secteur": "mixte",
                    "conseil": "Proposez la réservation de cadeaux en avance pour la Saint-Valentin. Réduisez le stress de dernière minute de vos clients.",
                    "tags": ["saisonnier", "service", "saint_valentin", "mixte"],
                    "niveau": "intermediaire"
                }
            ]
        }
    
    def get_seasonal_tips(self, secteur, type_commerce, experience_level):
        """Retourne les conseils saisonniers du mois actuel"""
        current_month = datetime.now().month
        monthly_tips = self.monthly_tips.get(current_month, [])
        
        # Filtre par secteur, type de commerce et niveau
        filtered_tips = [
            tip for tip in monthly_tips 
            if tip["secteur"] in [secteur, "mixte", "general"] 
            and tip.get("type_commerce", "all") in [type_commerce, "all"]
            and tip["niveau"] in [experience_level, "all"]
        ]
        
        return filtered_tips

seasonal_manager = SeasonalContent()