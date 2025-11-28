from data.database import db
from data.predefined_content import *
from data.seasonal_content import seasonal_manager
import random

class ContentManager:
    def __init__(self):
        self._initialize_content()
    
    def _initialize_content(self):
        """Initialise le contenu dans la base de données"""
        self._ensure_collection_exists('predefined_tips', PREDEFINED_TIPS)
        self._ensure_collection_exists('predefined_promos', PREDEFINED_PROMOS)
        self._ensure_collection_exists('inspirational_stories', INSPIRATIONAL_STORIES)
        self._ensure_collection_exists('motivation_messages', MOTIVATION_MESSAGES)
    
    def _ensure_collection_exists(self, collection_name, default_data):
        """S'assure qu'une collection existe avec des données par défaut"""
        collection = db.get_collection(collection_name)
        if collection.count_documents({}) == 0:
            collection.insert_many(default_data)
    
    def get_daily_tip(self, secteur, type_commerce, experience_level):
        """Retourne un conseil personnalisé avec priorité saisonnier"""
        # 1. Essaie d'abord les conseils saisonniers (70% de chance)
        seasonal_tips = seasonal_manager.get_seasonal_tips(secteur, type_commerce, experience_level)
        if seasonal_tips and random.random() < 0.7:
            return random.choice(seasonal_tips)
        
        # 2. Conseils par type de commerce
        commerce_tips = list(db.predefined_tips.find({
            "$or": [
                {"type_commerce": type_commerce},
                {"type_commerce": "all"},
                {"type_commerce": "mixte"}
            ],
            "$or": [
                {"secteur": secteur},
                {"secteur": "general"}
            ]
        }))
        
        if commerce_tips:
            # Priorise les conseils du même niveau
            level_tips = [t for t in commerce_tips if t.get('niveau') == experience_level]
            if level_tips:
                return random.choice(level_tips)
            return random.choice(commerce_tips)
        
        # 3. Fallback général
        return {
            "conseil": "Observez vos clients pour mieux comprendre leurs besoins et adaptez votre offre en conséquence.",
            "tags": ["general"],
            "secteur": "general",
            "type_commerce": "all"
        }
    
    def get_inspirational_story(self, secteur=None, type_commerce=None):
        """Retourne une histoire inspirante adaptée"""
        query = {}
        if secteur:
            query["secteur"] = secteur
        if type_commerce:
            query["type_commerce"] = type_commerce
            
        stories = list(db.inspirational_stories.find(query))
        
        if stories:
            return random.choice(stories)
        
        # Fallback général
        return {
            "personnage": "Un commerçant togolais",
            "histoire": "A persévéré malgré les difficultés et a réussi à développer son commerce grâce à la qualité constante et à l'adaptation aux besoins clients.",
            "lecon": "La persévérance et l'adaptation sont les clés du succès commercial"
        }
    
    def get_motivational_message(self):
        """Retourne un message de motivation"""
        messages = list(db.motivation_messages.find())
        if messages:
            return random.choice(messages)
        return {"message": "Continuez vos efforts, chaque jour compte ! 🌟"}
    
    def get_predefined_promos(self, promo_type, secteur, type_commerce):
        """Retourne des promotions pré-définies adaptées"""
        promos = list(db.predefined_promos.find({
            "type": promo_type,
            "$or": [
                {"secteur": secteur},
                {"secteur": "general"}
            ],
            "$or": [
                {"type_commerce": type_commerce},
                {"type_commerce": "all"}
            ]
        }))
        return promos

# Instance globale
content_manager = ContentManager()