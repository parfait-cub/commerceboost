import google.generativeai as genai
from utils.config import Config
from data.content_manager import content_manager
from datetime import datetime

# Configuration Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)

class HybridAIEngine:
    def __init__(self):
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        self.prompt_expert = """
Tu es CommerceBoost, expert en marketing et gestion commerciale spécialisé sur le Togo et l'Afrique de l'Ouest.

CONTEXTE SAISONNIER : Nous sommes en {current_month_name} {current_year}. {seasonal_context}

TYPE DE COMMERCE : {business_type_context}

TON RÔLE :
Conseiller les commerçants togolais selon leur type de commerce (physique, en ligne, ou mixte) avec des stratégies adaptées.

RÈGLES STRICTES :
- 🚫 INTERDIT d'inventer des noms de commerces, boutiques ou entreprises
- 🚫 INTERDIT de donner des prix, montants ou chiffres spécifiques  
- 🚫 INTERDIT de mentionner des lieux, marchés ou villes fictifs
- 🚫 INTERDIT de répondre à des questions hors marketing/gestion
- ✅ ADAPTER les conseils au type de commerce (physique/en ligne/mixte)
- ✅ TENIR COMPTE de la saisonnalité actuelle
- ✅ PRIVILÉGIER les stratégies adaptées au contexte togolais

EXEMPLES DE RÉPONSES ADAPTÉES :

Pour commerce PHYSIQUE :
"En boutique, vous pourriez rearranger votre vitrine pour mettre en valeur vos produits de saison"
"Formez votre personnel à accueillir chaleureusement chaque client qui entre"

Pour commerce EN LIGNE :
"Optimisez vos photos produits pour les réseaux sociaux fréquentés par votre clientèle"
"Mettez en place un système de réponse rapide aux messages sur WhatsApp"

Pour commerce MIXTE :
"Annoncez vos promotions à la fois en boutique et sur vos canaux digitaux"
"Proposez le retrait en boutique des commandes passées en ligne"

Si la question est hors sujet, répondre poliment :
"Je me concentre sur le marketing et la gestion pour vous aider au mieux. 😊"

QUESTION DE L'UTILISATEUR : {question}

CONTEXTE UTILISATEUR : {user_context}

Réponds en français, sois pratique et concret, et adapte tes conseils au type de commerce :
"""
    
    def get_seasonal_context(self):
        """Retourne le contexte saisonnier actuel"""
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        month_names = {
            1: "janvier", 2: "février", 3: "mars", 4: "avril",
            5: "mai", 6: "juin", 7: "juillet", 8: "août", 
            9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
        }
        
        seasonal_contexts = {
            12: "C'est la période des fêtes de fin d'année, les clients sont en recherche de cadeaux et de produits pour célébrer.",
            1: "Début d'année, période des soldes et des bonnes résolutions. Les clients cherchent des bonnes affaires.",
            2: "Mois de la Saint-Valentin, les clients recherchent des cadeaux romantiques et des attentions spéciales.",
            6: "Début de la saison des pluies, adaptez vos stocks et horaires en conséquence.",
            10: "Saison sèche qui approche, période généralement plus active pour le commerce."
        }
        
        current_month_name = month_names.get(current_month, "cette période de l'année")
        seasonal_context = seasonal_contexts.get(current_month, "Adaptez votre offre aux besoins actuels de vos clients.")
        
        return current_month_name, current_year, seasonal_context
    
    def get_business_type_context(self, business_type):
        """Retourne le contexte adapté au type de commerce"""
        contexts = {
            "physique": "L'utilisateur a un commerce physique (boutique, échoppe, restaurant). Concentrez-vous sur les stratégies pour attirer les clients en boutique, améliorer l'expérience en magasin, et optimiser la présentation physique.",
            "en_ligne": "L'utilisateur vend en ligne (e-commerce, réseaux sociaux, WhatsApp). Concentrez-vous sur les stratégies digitales, l'optimisation des photos, la communication sur les réseaux, et la logistique de livraison.",
            "mixte": "L'utilisateur vend à la fois en physique et en ligne. Proposez des stratégies intégrées qui combinent les avantages des deux canaux."
        }
        return contexts.get(business_type, "Adaptez vos conseils au type de commerce de l'utilisateur.")
    
    def generate_response(self, user_question, user_context, business_type="physique"):
        """Génère une réponse IA adaptée au type de commerce"""
        # Vérifie si la question est hors sujet
        if self._is_off_topic(user_question):
            return "Je me concentre sur le marketing et la gestion pour vous aider au mieux. 😊"
        
        try:
            current_month_name, current_year, seasonal_context = self.get_seasonal_context()
            business_type_context = self.get_business_type_context(business_type)
            
            prompt = self.prompt_expert.format(
                current_month_name=current_month_name,
                current_year=current_year,
                seasonal_context=seasonal_context,
                business_type_context=business_type_context,
                question=user_question,
                context=user_context
            )
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return "Je rencontre un problème technique. Pouvez-vous reformuler votre question ?"
    
    def _is_off_topic(self, question):
        """Vérifie si la question est hors sujet"""
        off_topic_keywords = [
            'réparer', 'technique', 'médical', 'politique', 'religion',
            'personnel', 'légal', 'juridique', 'santé', 'amour', 'familial',
            'sport', 'divertissement', 'actualité', 'météo'
        ]
        
        on_topic_keywords = [
            'vendre', 'marketing', 'client', 'stock', 'prix', 'marge',
            'profit', 'commerce', 'business', 'vente', 'fidélisation',
            'promotion', 'communication', 'stratégie', 'concurrent',
            'produit', 'service', 'gestion', 'inventaire', 'achat',
            'budget', 'croissance', 'développement', 'planification',
            'boutique', 'magasin', 'en ligne', 'digital', 'physique',
            'site', 'réseaux sociaux', 'whatsapp', 'facebook', 'instagram',
            'vitrine', 'présentation', 'livraison', 'commande'
        ]
        
        question_lower = question.lower()
        
        # Si contient des mots interdits
        if any(word in question_lower for word in off_topic_keywords):
            return True
        
        # Si ne contient pas de mots pertinents
        if not any(word in question_lower for word in on_topic_keywords):
            return True
        
        return False

# Instance globale
ai_engine = HybridAIEngine()