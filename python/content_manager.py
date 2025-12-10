# python/content_manager.py
import google.generativeai as genai
from utils.config import Config
from datetime import datetime
import calendar

# Configuration
genai.configure(api_key=Config.GEMINI_API_KEY)

class CommerceBoostExpert:
    def __init__(self):
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config={
                "temperature": 0.75,
                "top_p": 0.85,
                "top_k": 40,
                "max_output_tokens": 900,
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            ]
        )

        self.PROMPT_EXPERT = """
Tu es Maître Koffi, 23 ans d’expérience à Lomé. Tu as boosté 3 000 commerçants de 300 000 à 3 millions FCFA/mois.

RÈGLES D’OR (violation = viré) :
- Jamais de prix, chiffres exacts, noms inventés
- Jamais politique, religion, santé, amour, sport
- Toujours 100 % adapté au type (physique / en ligne / mixte), secteur, niveau
- Toujours psychologie togolaise : honte d’hésiter, besoin de se sentir VIP, urgence subtile
- Anomalies climatiques Sud Togo : pluies irrégulières, sécheresse précoce, hausse températures → conseille adaptations flexibles, surveillance locale

MOIS : {current_month_name} {current_year} → {seasonal_context}
TYPE : {business_type} | Secteur : {sector} | Niveau : {level}

QUESTION : {question}

CONTEXTE : {user_context}

Réponds en français togolais naturel, direct, chaleureux.
Donne 1-2 actions puissantes pour demain matin.
Termine par une phrase motivante courte et forte.

EXEMPLES PSYCHOLOGIQUES & SAISONNIERS AVANCÉS :
Physique → « Frère, le Togolais hésite par honte. Dis : 'C’est pour offrir ? Tu as bon goût !' → il achète pour se valoriser. En pluies irrégulières, couvre ta vitrine vite, dis 'Viens te protéger ici, on discute'. »
En ligne → « Crée urgence : 'Dernier en stock, je le garde pour toi ?' → même s’il reste beaucoup. Avec sécheresse précoce, poste 'Protège-toi de la chaleur avec ça, livraison express'. »
Mixte → « Fais VIP : 'Code secret boutique pour clients WhatsApp' → sentiment d’exclusivité. En anomalies climatiques, adapte stocks jour/jour : 'Aujourd’hui pluie ? Promo abritée en boutique'. »
Physique (saison avancée) → « En hausse températures, offre eau fraîche à l’entrée → client reste plus, parle plus, achète plus par gratitude. »
En ligne (psycho) → « Quand silence radio, envoie : 'Je pense à toi, ça te va ?' → brise la barrière émotionnelle togolaise. »
Mixte (saison) → « Pluies tardives ? Poste en ligne 'Commande maintenant, retire sec en boutique' → exploite peur de se mouiller. »

Vas-y Maître Koffi, fais-le gagner avec des secrets rares.
"""

    def get_seasonal_context(self):
        month = datetime.now().month
        year = datetime.now().year
        mois = ["", "janvier", "février", "mars", "avril", "mai", "juin",
                "juillet", "août", "septembre", "octobre", "novembre", "décembre"][month]
        
        saison = {
            1: "Début d’année, argent frais, achats impulsifs – surveille anomalies pour stocks flexibles",
            2: "Saint-Valentin, cadeaux & séduction – adapte à pluies imprévues",
            3: "Poussière & chaleur – prépare pour sécheresse précoce",
            6: "Pluies théoriques – mais irrégulières, focus livraison",
            8: "Rentrée scolaire = boom – malgré températures hautes",
            12: "Noël → achats émotionnels – gère variabilité climatique"
        }.get(month, "Période normale, fidélisation maximale – reste vigilant aux anomalies Sud Togo")
        
        return mois, year, saison

    def generate_response(self, question: str, user_context: dict):
        if not question or not question.strip():
            return "Pose-moi ta question, je suis là pour t’aider à booster ton commerce !"

        # Sécurité anti-hors-sujet
        off_topic = ['politique', 'élection', 'docteur', 'maladie', 'médicament', 'dieu', 'prière', 'amour', 'couple', 'foot', 'match']
        if any(word in question.lower() for word in off_topic):
            return "Je me concentre uniquement sur le commerce et le marketing pour t’aider à gagner plus. Pose-moi une question sur ton business !"

        try:
            month_name, year, seasonal = self.get_seasonal_context()

            business_type = user_context.get('business_type', 'physique')
            sector = user_context.get('sector', 'général')
            level = user_context.get('level', 'débutant')

            prompt = self.PROMPT_EXPERT.format(
                current_month_name=month_name,
                current_year=year,
                seasonal_context=seasonal,
                business_type=business_type,
                sector=sector.capitalize(),
                level=level.capitalize(),
                question=question,
                user_context=user_context
            )

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            return "Maître Koffi a un petit problème technique… Réessaie dans 10 secondes, je reviens plus fort !"

# Instance globale à importer partout
expert_ai = CommerceBoostExpert()