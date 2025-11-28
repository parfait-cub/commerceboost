from flask import request, jsonify
import requests
import json
from data.database import db
from data.content_manager import content_manager
from ai.margin_calculator import margin_calculator
from ai.promo_generator import promo_generator
from ai.hybrid_engine import ai_engine
from utils.config import Config
from utils.referral_system import referral_system
from datetime import datetime, timedelta

class MessengerBot:
    def __init__(self):
        self.page_access_token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        self.api_url = f"https://graph.facebook.com/v18.0/me/messages?access_token={self.page_access_token}"
        self.referral_system = referral_system
    
    def handle_message(self, data):
        """Gère les messages entrants"""
        if data.get("object") != "page":
            return jsonify({"status": "error"}), 404
        
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                message_text = self._extract_message_text(messaging_event)
                
                if message_text:
                    self.process_user_message(sender_id, message_text)
                
        return jsonify({"status": "ok"}), 200
    
    def _extract_message_text(self, messaging_event):
        """Extrait le texte du message"""
        if "message" in messaging_event and "text" in messaging_event["message"]:
            return messaging_event["message"]["text"].strip()
        return None
    
    def process_user_message(self, user_id, message):
        """Traite le message de l'utilisateur"""
        user = self.get_or_create_user(user_id)
        
        # Sauvegarde la conversation
        db.conversations.insert_one({
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.now(),
            "direction": "incoming"
        })
        
        # Gestion de l'onboarding amélioré
        if user.get('onboarding_step') == 'waiting_business_type':
            self.handle_business_type_selection(user_id, message)
            return
        
        elif user.get('onboarding_step') == 'waiting_sector':
            self.handle_sector_selection(user_id, message)
            return
        
        elif user.get('onboarding_step') == 'waiting_experience':
            self.handle_experience_selection(user_id, message)
            return
        
        # Traitement des commandes spéciales
        if message.lower() in ["start", "bonjour", "salut", "hello"]:
            self.send_welcome_message(user_id)
        elif message.lower() in ["calculer marge", "marge", "🧮"]:
            self.start_margin_calculator(user_id)
        elif message.lower() in ["promotion", "promo", "🎁"]:
            self.start_promo_generator(user_id)
        elif message.lower() in ["mes outils", "outils", "🛠️"]:
            self.show_tools_dashboard(user_id)
        elif message.lower() in ["abonnement", "formules", "prix", "payer"]:
            self.handle_subscription_selection(user_id, message)
        elif message.isdigit() and len(message) <= 2:
            self.handle_menu_selection(user_id, message, user)
        else:
            self.handle_regular_message(user_id, message, user)
    
    def get_or_create_user(self, user_id):
        """Récupère ou crée un utilisateur"""
        user = db.users.find_one({"user_id": user_id})
        
        if not user:
            # Récupère les infos du profil Facebook
            profile_info = self.get_user_profile(user_id)
            
            user_data = {
                "user_id": user_id,
                "name": profile_info.get("name", "Utilisateur"),
                "first_name": profile_info.get("first_name", ""),
                "last_name": profile_info.get("last_name", ""),
                "created_at": datetime.now(),
                "trial_ends_at": datetime.now() + timedelta(days=Config.TRIAL_DAYS),
                "subscription_tier": "trial",
                "status": "active",
                "onboarding_step": "not_started",
                "profile_data": profile_info
            }
            
            db.users.insert_one(user_data)
            return user_data
        
        return user
    
    def get_user_profile(self, user_id):
        """Récupère le profil Facebook de l'utilisateur"""
        try:
            url = f"https://graph.facebook.com/v18.0/{user_id}"
            params = {
                "access_token": Config.FACEBOOK_PAGE_ACCESS_TOKEN,
                "fields": "first_name,last_name,name,profile_pic"
            }
            response = requests.get(url, params=params)
            return response.json()
        except:
            return {}
    
    def send_welcome_message(self, user_id):
        """Envoie le message de bienvenue"""
        welcome_message = f"""
👋 Bonjour ! Je suis CommerceBoost, votre assistant marketing intelligent pour commerçants togolais.

Je vous aide à :
• 📈 Augmenter vos ventes (physique & en ligne)
• 🎯 Attirer plus de clients  
• 💰 Optimiser vos marges
• 🎁 Créer des promotions efficaces

Par où commençons-nous ?

1 🆓 ESSAI GRATUIT {Config.TRIAL_DAYS} jours
2 🧮 CALCULER ma marge
3 🎁 CRÉER une promotion
4 💬 POSER une question

Répondez avec le chiffre ou l'emoji !
        """
        
        self.send_text_message(user_id, welcome_message)
    
    def start_margin_calculator(self, user_id):
        """Démarre le calculateur de marge"""
        message = """
🧮 **CALCULETTE MARGE RAPIDE**

Je peux vous aider à calculer votre marge en 30 secondes !

Envoyez-moi vos prix dans ce format :

💰 **Prix d'achat** - **Prix de vente**

Exemple : 1000 - 1500

Ou tapez 'exemple' pour voir un calcul type.
        """
        self.send_text_message(user_id, message)
    
    def start_promo_generator(self, user_id):
        """Démarre le générateur de promotions"""
        user = db.users.find_one({"user_id": user_id})
        business_type = user.get("business_type", "physique")
        
        message = f"""
🎁 **GÉNÉRATEUR DE PROMOTIONS** {'🛍️' if business_type == 'physique' else '📱' if business_type == 'en_ligne' else '🔀'}

Je vais vous créer une promo adaptée à votre commerce {business_type.replace('_', ' ')} !

Quel type d'offre souhaitez-vous ?
1️⃣ 📉 Pour écouler un stock lent
2️⃣ 🎯 Pour attirer nouveaux clients  
3️⃣ 💝 Pour fidéliser clients existants
4️⃣ 🚀 Pour lancer un nouveau produit

Répondez avec le chiffre ou l'emoji !
        """
        self.send_text_message(user_id, message)
    
    def show_tools_dashboard(self, user_id):
        """Affiche le tableau de bord des outils"""
        user = db.users.find_one({"user_id": user_id})
        business_type = user.get("business_type", "non spécifié")
        
        message = f"""
🛠️ **VOS OUTILS COMMERCEBOOST** ({business_type.upper()})

Choisissez un outil :

🧮 Calculette de marge
🎁 Générateur de promotions  
📊 Mes promotions sauvegardées
💡 Conseils selon ma marge
📈 Mes calculs récents

Tapez le nom de l'outil qui vous intéresse !
        """
        self.send_text_message(user_id, message)
    
    def handle_menu_selection(self, user_id, selection, user):
        """Gère les sélections de menu"""
        if selection == "1":
            self.start_user_onboarding(user_id)
        elif selection == "2":
            self.start_margin_calculator(user_id)
        elif selection == "3":
            self.start_promo_generator(user_id)
        elif selection == "4":
            self.ask_question_prompt(user_id)
        else:
            self.send_text_message(user_id, "Choix non reconnu. Tapez 'start' pour recommencer.")
    
    def start_user_onboarding(self, user_id):
        """Démarre le processus d'onboarding amélioré"""
        # Met à jour l'étape d'onboarding
        db.users.update_one(
            {"user_id": user_id},
            {"$set": {"onboarding_step": "waiting_business_type"}}
        )
        
        message = f"""
🎉 Excellent choix ! Votre essai gratuit de {Config.TRIAL_DAYS} jours est activé !

Pour personnaliser vos conseils, dites-moi :

**1️⃣ Quel type de commerce avez-vous ?**
🏪 PHYSIQUE (boutique, restaurant, marché...)
🌐 EN LIGNE (e-commerce, réseaux sociaux, WhatsApp...)
📱 LES DEUX (vous vendez en boutique ET en ligne)

Répondez avec l'emoji ou le texte !
        """
        self.send_text_message(user_id, message)
    
    def handle_business_type_selection(self, user_id, message):
        """Gère la sélection du type de commerce"""
        business_type_map = {
            "🏪": "physique", "physique": "physique", "boutique": "physique", "magasin": "physique",
            "🌐": "en_ligne", "ligne": "en_ligne", "en ligne": "en_ligne", "digital": "en_ligne",
            "📱": "mixte", "deux": "mixte", "les deux": "mixte", "mixte": "mixte"
        }
        
        selected_type = None
        message_lower = message.lower()
        
        for key, business_type in business_type_map.items():
            if key in message or key.lower() in message_lower:
                selected_type = business_type
                break
        
        if selected_type:
            # Met à jour le type de commerce
            db.users.update_one(
                {"user_id": user_id},
                {"$set": {
                    "business_type": selected_type,
                    "onboarding_step": "waiting_sector"
                }}
            )
            self.ask_business_sector(user_id)
        else:
            self.send_text_message(user_id, "Je n'ai pas compris. Choisissez 🏪 Physique, 🌐 En ligne ou 📱 Les deux")
    
    def ask_business_sector(self, user_id):
        """Demande le secteur d'activité"""
        message = """
**2️⃣ Quel est votre secteur principal ?**
🍕 Alimentation (restaurant, épicerie, produits frais...)
👕 Mode & Vêtements (vêtements, chaussures, accessoires...)
💄 Beauté & Cosmétiques (coiffure, maquillage, soins...)
📱 Électronique & Téléphonie (téléphones, accessoires, recharge...)
🏠 Maison & Décoration (meubles, décoration, électroménager...)
➕ Autre (spécifiez dans votre réponse)

Répondez avec l'emoji !
        """
        self.send_text_message(user_id, message)
    
    def handle_sector_selection(self, user_id, message):
        """Gère la sélection du secteur"""
        sector_map = {
            "🍕": "alimentaire", "nourriture": "alimentaire", "restaurant": "alimentaire",
            "👕": "mode", "vêtements": "mode", "habillement": "mode", "textile": "mode",
            "💄": "beaute", "cosmétiques": "beaute", "coiffure": "beaute", "soins": "beaute",
            "📱": "electronique", "téléphonie": "electronique", "électronique": "electronique",
            "🏠": "maison", "décoration": "maison", "meubles": "maison", "electroménager": "maison",
            "➕": "autre", "divers": "autre", "autre": "autre"
        }
        
        selected_sector = None
        message_lower = message.lower()
        
        for key, sector in sector_map.items():
            if key in message or key.lower() in message_lower:
                selected_sector = sector
                break
        
        if selected_sector:
            # Met à jour le secteur
            db.users.update_one(
                {"user_id": user_id},
                {"$set": {
                    "sector": selected_sector,
                    "onboarding_step": "waiting_experience"
                }}
            )
            self.ask_experience_level(user_id)
        else:
            self.send_text_message(user_id, "Je n'ai pas compris. Choisissez un secteur avec l'emoji correspondant")
    
    def ask_experience_level(self, user_id):
        """Demande le niveau d'expérience"""
        message = """
**3️⃣ Depuis combien de temps vendez-vous ?**
🟢 DÉBUTANT (moins de 6 mois)
🟡 INTERMÉDIAIRE (6 mois - 2 ans)  
🔴 EXPÉRIMENTÉ (plus de 2 ans)

Répondez avec l'emoji ou le texte !
        """
        self.send_text_message(user_id, message)
    
    def handle_experience_selection(self, user_id, message):
        """Gère la sélection du niveau d'expérience"""
        experience_map = {
            "🟢": "debutant", "débutant": "debutant", "nouveau": "debutant", "commence": "debutant",
            "🟡": "intermediaire", "intermédiaire": "intermediaire", "moyen": "intermediaire",
            "🔴": "experimente", "expérimenté": "experimente", "expérimente": "experimente", "ancien": "experimente"
        }
        
        selected_experience = None
        message_lower = message.lower()
        
        for key, experience in experience_map.items():
            if key in message or key.lower() in message_lower:
                selected_experience = experience
                break
        
        if selected_experience:
            self.complete_onboarding(user_id, selected_experience)
        else:
            self.send_text_message(user_id, "Je n'ai pas compris. Choisissez 🟢 Débutant, 🟡 Intermédiaire ou 🔴 Expérimenté")
    
    def complete_onboarding(self, user_id, experience_level):
        """Termine l'onboarding et envoie le premier conseil"""
        # Met à jour l'expérience et termine l'onboarding
        db.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "experience": experience_level,
                "onboarding_step": "completed",
                "onboarding_completed_at": datetime.now()
            }}
        )
        
        # CRÉATION DU CODE DE PARRAINAGE (NOUVEAU)
        referral_code = self.referral_system.create_referral_for_user(user_id)
        
        user = db.users.find_one({"user_id": user_id})
        business_type = user.get("business_type", "physique")
        sector = user.get("sector", "general")
        
        # Envoie le premier conseil personnalisé
        tip = content_manager.get_daily_tip(sector, business_type, experience_level)
        story = content_manager.get_inspirational_story(sector, business_type)
        motivation = content_manager.get_motivational_message()
        
        # Texte adapté au type de commerce
        business_type_text = {
            "physique": "en boutique 🏪",
            "en_ligne": "en ligne 🌐", 
            "mixte": "en boutique ET en ligne 📱"
        }
        
        welcome_message = f"""
🎯 **ONBOARDING TERMINÉ !**

Bienvenue dans la famille CommerceBoost !

Votre profil :
🏢 Type : {business_type_text.get(business_type, business_type)}
📊 Secteur : {sector.upper()}
🎓 Expérience : {experience_level.upper()}
🆓 Essai : {Config.TRIAL_DAYS} jours

🎁 **VOTRE CODE DE PARRAINAGE : {referral_code}**
Partagez-le à vos amis commerçants et gagnez -{int(Config.REFERRAL_DISCOUNT * 100)}% chacun !

📅 **VOTRE PREMIER CONSEIL PERSONNALISÉ**

{tip['conseil']}

📖 **HISTOIRE INSPIRANTE**
{story['histoire']}
💡 *Leçon : {story['lecon']}*

💪 **MOTIVATION**
{motivation['message']}

👉 Vous recevrez un nouveau conseil personnalisé chaque matin à 8h !

Tapez 'outils' pour découvrir tous mes outils ou posez-moi une question !
        """
        
        self.send_text_message(user_id, welcome_message)
    
    def ask_question_prompt(self, user_id):
        """Invite à poser une question"""
        self.send_text_message(user_id, "💬 Quelle question marketing ou gestion avez-vous ? Je suis là pour vous aider !")
    
    def handle_regular_message(self, user_id, message, user):
        """Traite les messages réguliers"""
        # Vérifie si c'est un calcul de marge
        if "-" in message and any(char.isdigit() for char in message):
            parts = message.split("-")
            if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
                prix_achat = parts[0].strip()
                prix_vente = parts[1].strip()
                result = margin_calculator.calculate_margin(user_id, prix_achat, prix_vente)
                
                if "error" not in result:
                    response = f"""
🧮 **RÉSULTAT DU CALCUL**

💰 Prix d'achat : {prix_achat} FCFA
🏷️ Prix de vente : {prix_vente} FCFA
📊 Marge brute : {result['marge_brute']} FCFA
📈 Pourcentage de marge : {result['pourcentage_marge']}%

💡 **Conseil** : {result['conseil']}

📝 Calcul sauvegardé dans votre historique !
                    """
                else:
                    response = "❌ Format incorrect. Utilisez : prix_achat - prix_vente (ex: 1000 - 1500)"
                
                self.send_text_message(user_id, response)
                return
        
        # Vérifie les sélections de promotions
        promo_selections = {
            "1": "stock_lent",
            "2": "nouveaux_clients", 
            "3": "fidelisation",
            "4": "lancement"
        }
        
        if message in promo_selections:
            sector = user.get("sector", "general")
            business_type = user.get("business_type", "physique")
            promo = promo_generator.generate_promotion(user_id, promo_selections[message], sector, business_type)
            
            response = f"""
🎁 **PROMOTION GÉNÉRÉE POUR VOUS** ({business_type.replace('_', ' ').upper()})

**{promo['titre']}**

📝 {promo['description']}

✅ **Avantage** : {promo['avantage']}

💡 **Exemple** : {promo['exemple']}

📊 Cette promotion a été sauvegardée dans vos outils !
            """
            self.send_text_message(user_id, response)
            return
        
        # Vérifie le code de parrainage (NOUVEAU)
        if len(message) == 10 and message.startswith("BOOST"):
            result = self.referral_system.apply_referral(user_id, message)
            if result["success"]:
                response = f"""
🎉 **PARRAINAGE APPLIQUÉ !**

Vous venez d'être parrainé par {result['referrer_name']} !

✅ Vous bénéficiez maintenant de -{result['discount_percent']}% sur votre premier abonnement
✅ Votre parrain bénéficie aussi de -{result['discount_percent']}%

C'est gagnant-gagnant ! 🎯

Tapez 'abonnement' pour voir vos nouvelles réductions !
                """
            else:
                response = f"❌ {result['error']}"
            
            self.send_text_message(user_id, response)
            return
        
        # Outils dashboard
        if "calculette" in message.lower() or "marge" in message.lower() or "🧮" in message:
            self.start_margin_calculator(user_id)
            return
        elif "promotion" in message.lower() or "promo" in message.lower() or "🎁" in message:
            self.start_promo_generator(user_id)
            return
        
        # Sinon, utilise l'IA hybride adaptée au type de commerce
        business_type = user.get("business_type", "physique")
        user_context = f"Secteur: {user.get('sector', 'non spécifié')}, Expérience: {user.get('experience', 'débutant')}, Type: {business_type}"
        response = ai_engine.generate_response(message, user_context, business_type)
        self.send_text_message(user_id, response)
    
    def handle_subscription_selection(self, user_id, message):
        """Gère la sélection d'abonnement avec réductions"""
        plan_prices = {
            "demarrage": Config.DEMARRAGE_PRICE,
            "croissance": Config.CROISSANCE_PRICE, 
            "elite": Config.ELITE_PRICE
        }
        
        plan_names = {
            "demarrage": "DÉMARRAGE",
            "croissance": "CROISSANCE",
            "elite": "ELITE"
        }
        
        if message.lower() in ["abonnement", "formules", "prix"]:
            base_price = plan_prices["demarrage"]
            final_price = self.referral_system.calculate_final_price(user_id, base_price)
            discounts = self.referral_system.get_applicable_discounts(user_id)
            
            discount_text = ""
            if discounts:
                discount_text = "\n🎁 **VOS RÉDUCTIONS APPLICABLES :**\n"
                for discount in discounts:
                    discount_text += f"• {discount['description']}\n"
            
            message_text = f"""
💰 **FORMULES DISPONIBLES** {discount_text}

🚀 DÉMARRAGE : {plan_prices['demarrage']} FCFA → {final_price:.0f} FCFA
📈 CROISSANCE : {plan_prices['croissance']} FCFA  
💎 ELITE : {plan_prices['elite']} FCFA

💡 *Exemple pour DÉMARRAGE :*
Prix normal : {plan_prices['demarrage']} FCFA
Avec vos réductions : {final_price:.0f} FCFA

Choisissez une formule en tapant son nom !
            """
            self.send_text_message(user_id, message_text)
            return
        
        # Gestion de la sélection de formule
        selected_plan = None
        for plan in plan_prices.keys():
            if plan in message.lower():
                selected_plan = plan
                break
        
        if selected_plan:
            self.show_plan_confirmation(user_id, selected_plan)
            return
    
    def show_plan_confirmation(self, user_id, plan):
        """Affiche la confirmation d'abonnement avec réductions"""
        plan_prices = {
            "demarrage": Config.DEMARRAGE_PRICE,
            "croissance": Config.CROISSANCE_PRICE,
            "elite": Config.ELITE_PRICE
        }
        
        plan_names = {
            "demarrage": "DÉMARRAGE",
            "croissance": "CROISSANCE", 
            "elite": "ELITE"
        }
        
        base_price = plan_prices[plan]
        final_price = self.referral_system.calculate_final_price(user_id, base_price)
        discounts = self.referral_system.get_applicable_discounts(user_id)
        
        discount_text = "\n📉 **RÉDUCTIONS APPLIQUÉES :**\n"
        current_price = base_price
        for discount in discounts:
            discount_amount = current_price * discount["value"]
            current_price -= discount_amount
            discount_text += f"• {discount['description']} : -{discount_amount:.0f} FCFA\n"
        
        message = f"""
✅ **CONFIRMATION ABONNEMENT {plan_names[plan]}**

💰 Prix de base : {base_price} FCFA
{discount_text}
🎯 **PRIX FINAL : {final_price:.0f} FCFA**

📱 **PROCÉDURE DE PAIEMENT :**
1. Envoyez {final_price:.0f} FCFA via Flooz/TMoney
2. Votre abonnement sera activé automatiquement
3. Continuez à recevoir vos conseils personnalisés

💳 Envoyer à :
• FLOOZ : 96 51 11 60 
• T-MONEY : 71 40 70 19

📞 Gardez les SMS activés pour validation automatique

Tapez 'confirmer' pour valider ou 'annuler' pour changer.
        """
        self.send_text_message(user_id, message)
    
    def send_trial_reminder(self, user_id, days_left):
        """Envoie un rappel d'essai avec offre de parrainage"""
        user = db.users.find_one({"user_id": user_id})
        if not user:
            return
        
        referral_code = user.get("referral_code", "N/A")
        
        if days_left == 3:
            message = f"""
⏰ **RAPPEL ESSAI GRATUIT**

Il vous reste {days_left} jours d'essai gratuit !

🎁 **GAGNEZ -{int(Config.REFERRAL_DISCOUNT * 100)}% AVEC LE PARRAINAGE**
Partagez votre code à d'autres commerçants :

**{referral_code}**

Pour chaque ami qui s'inscrit avec votre code :
✅ Vous gagnez -{int(Config.REFERRAL_DISCOUNT * 100)}% sur votre abonnement
✅ Votre ami gagne -{int(Config.REFERRAL_DISCOUNT * 100)}% aussi

C'est gagnant-gagnant ! 🎯
            """
        
        elif days_left == 1:
            message = f"""
🚨 **DERNIER JOUR D'ESSAI !**

C'est votre dernier jour d'essai gratuit !

💰 **ABONNEZ-VOUS MAINTENANT ET ÉCONOMISEZ**
Avec votre code de parrainage utilisé, vous pouvez avoir jusqu'à -{int((Config.REFERRAL_DISCOUNT + Config.WELCOME_DISCOUNT) * 100)}% !

Tapez 'abonnement' pour voir les formules et vos réductions.
            """
        
        else:
            return
        
        self.send_text_message(user_id, message)
    
    def send_text_message(self, recipient_id, message_text):
        """Envoie un message texte"""
        message_data = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }
        
        # Sauvegarde en base
        db.conversations.insert_one({
            "user_id": recipient_id,
            "message": message_text,
            "timestamp": datetime.now(),
            "direction": "outgoing"
        })
        
        # Envoi via Facebook
        try:
            response = requests.post(
                self.api_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(message_data)
            )
            return response.json()
        except Exception as e:
            print(f"Erreur envoi message: {e}")
            return None
    
    def send_daily_tip(self, user_id):
        """Envoie le conseil quotidien amélioré"""
        user = db.users.find_one({"user_id": user_id})
        if not user or user.get("onboarding_step") != "completed":
            return
        
        sector = user.get("sector", "general")
        business_type = user.get("business_type", "physique")
        experience = user.get("experience", "debutant")
        
        # Récupère le conseil adapté
        tip = content_manager.get_daily_tip(sector, business_type, experience)
        
        # Récupère une histoire inspirante adaptée
        story = content_manager.get_inspirational_story(sector, business_type)
        
        # Récupère un message de motivation
        motivation = content_manager.get_motivational_message()
        
        message = f"""
📅 **VOTRE CONSEIL COMMERCEBOOST DU JOUR** ({business_type.replace('_', ' ').upper()})

🎯 {tip['conseil']}

📖 **HISTOIRE INSPIRANTE**
{story['histoire']}
💡 *Leçon : {story['lecon']}*

💪 **MOTIVATION**
{motivation['message']}

👉 Essayez ce conseil aujourd'hui et revenez me dire !
        """
        
        self.send_text_message(user_id, message)

# Instance globale
messenger_bot = MessengerBot()