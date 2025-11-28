import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from data.database import db
from utils.config import Config
from datetime import datetime, timedelta

class TelegramAdminBot:
    def __init__(self):
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.admin_users = Config.ADMIN_USER_IDS
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /start pour admin"""
        user_id = update.effective_user.id
        
        if user_id not in self.admin_users:
            await update.message.reply_text("❌ Accès non autorisé.")
            return
        
        keyboard = [
            [InlineKeyboardButton("👥 Utilisateurs", callback_data="users")],
            [InlineKeyboardButton("💰 Paiements", callback_data="payments")],
            [InlineKeyboardButton("📊 Statistiques", callback_data="stats")],
            [InlineKeyboardButton("🎁 Promotions", callback_data="promotions")],
            [InlineKeyboardButton("📢 Message groupé", callback_data="broadcast")],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔧 **PANEL ADMIN COMMERCEBOOST**\n\n"
            "Choisissez une option :",
            reply_markup=reply_markup
        )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère les clics sur les boutons"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if user_id not in self.admin_users:
            await query.edit_message_text("❌ Accès non autorisé.")
            return
        
        data = query.data
        
        if data == "users":
            await self.show_users_menu(query)
        elif data == "payments":
            await self.show_payments_menu(query)
        elif data == "stats":
            await self.show_general_stats(query)
        elif data == "promotions":
            await self.show_promotions_menu(query)
        elif data == "broadcast":
            await self.start_broadcast(query, context)
        elif data.startswith("user_detail_"):
            user_id = data.replace("user_detail_", "")
            await self.show_user_detail(query, user_id)
        elif data.startswith("validate_"):
            payment_id = data.replace("validate_", "")
            await self.validate_payment(query, payment_id)
        elif data == "payments_pending":
            await self.show_pending_payments(query)
        elif data == "back_main":
            await self.show_main_menu(query)
    
    async def show_users_menu(self, query):
        """Affiche le menu utilisateurs"""
        total_users = db.users.count_documents({})
        active_users = db.users.count_documents({"status": "active"})
        trial_users = db.users.count_documents({"subscription_tier": "trial"})
        completed_onboarding = db.users.count_documents({"onboarding_step": "completed"})
        
        keyboard = [
            [InlineKeyboardButton("📋 Liste utilisateurs", callback_data="users_list")],
            [InlineKeyboardButton("✅ Onboarding complet", callback_data="users_completed")],
            [InlineKeyboardButton("🆕 Essais gratuits", callback_data="users_trial")],
            [InlineKeyboardButton("🔙 Retour", callback_data="back_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"👥 **GESTION UTILISATEURS**\n\n"
            f"• Total utilisateurs : {total_users}\n"
            f"• Utilisateurs actifs : {active_users}\n"
            f"• Onboarding complet : {completed_onboarding}\n"
            f"• Essais en cours : {trial_users}\n\n"
            "Choisissez une option :",
            reply_markup=reply_markup
        )
    
    async def show_payments_menu(self, query):
        """Affiche le menu des paiements"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        total_payments = db.payments.count_documents({})
        today_payments = db.payments.count_documents({"payment_date": {"$gte": today}})
        pending_payments = db.payments.count_documents({"status": "pending"})
        
        revenue_today = sum([p.get('amount', 0) for p in db.payments.find({"payment_date": {"$gte": today}})])
        total_revenue = sum([p.get('amount', 0) for p in db.payments.find({})])
        
        keyboard = [
            [InlineKeyboardButton("⏳ Paiements en attente", callback_data="payments_pending")],
            [InlineKeyboardButton("✅ Paiements validés", callback_data="payments_verified")],
            [InlineKeyboardButton("📊 Statistiques revenus", callback_data="payments_stats")],
            [InlineKeyboardButton("🔄 Valider paiement manuel", callback_data="validate_manual")],
            [InlineKeyboardButton("🔙 Retour", callback_data="back_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"💰 **GESTION PAIEMENTS**\n\n"
            f"• Paiements aujourd'hui : {today_payments}\n"
            f"• Paiements en attente : {pending_payments}\n"
            f"• Total paiements : {total_payments}\n"
            f"• Revenue aujourd'hui : {revenue_today:,} FCFA\n"
            f"• Revenue total : {total_revenue:,} FCFA\n\n"
            "Choisissez une option :",
            reply_markup=reply_markup
        )
    
    async def show_pending_payments(self, query):
        """Affiche les paiements en attente avec boutons de validation"""
        pending_payments = list(db.payments.find({"status": "pending"}).limit(10))
        
        if not pending_payments:
            keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="payments")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("✅ Aucun paiement en attente.", reply_markup=reply_markup)
            return
        
        message = "⏳ **PAIEMENTS EN ATTENTE**\n\n"
        keyboard = []
        
        for payment in pending_payments:
            user = db.users.find_one({"user_id": payment["user_id"]})
            user_name = user.get("name", "N/A") if user else "Utilisateur inconnu"
            
            message += f"• {user_name} - {payment.get('amount', 0)} FCFA - {payment.get('plan', 'N/A')}\n"
            
            # Bouton pour valider ce paiement
            keyboard.append([
                InlineKeyboardButton(
                    f"✅ Valider {user_name}", 
                    callback_data=f"validate_{payment['_id']}"
                )
            ])
    
        keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data="payments")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
    
    async def validate_payment(self, query, payment_id):
        """Valide un paiement via bouton"""
        from bson.objectid import ObjectId
        
        try:
            payment = db.payments.find_one({"_id": ObjectId(payment_id)})
            
            if not payment:
                await query.answer("Paiement non trouvé")
                return
            
            # Met à jour le statut du paiement
            db.payments.update_one(
                {"_id": ObjectId(payment_id)},
                {"$set": {"status": "verified", "verified_at": datetime.now()}}
            )
            
            # Met à jour l'abonnement de l'utilisateur
            user_id = payment["user_id"]
            plan = payment.get("plan", "demarrage")
            
            db.users.update_one(
                {"user_id": user_id},
                {"$set": {
                    "subscription_tier": plan,
                    "subscription_ends_at": datetime.now() + timedelta(days=30),
                    "status": "active"
                }}
            )
            
            await query.answer(f"✅ Paiement validé ! Abonnement {plan} activé.")
            
            # Retourne au menu des paiements
            await self.show_payments_menu(query)
            
        except Exception as e:
            await query.answer(f"❌ Erreur: {str(e)}")
    
    async def show_general_stats(self, query):
        """Affiche les statistiques générales"""
        # Statistiques utilisateurs
        total_users = db.users.count_documents({})
        new_today = db.users.count_documents({"created_at": {"$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}})
        completed_onboarding = db.users.count_documents({"onboarding_step": "completed"})
        
        # Statistiques par type de commerce
        business_types = db.users.aggregate([
            {"$group": {"_id": "$business_type", "count": {"$sum": 1}}}
        ])
        
        business_stats = ""
        for bt in business_types:
            if bt['_id']:
                business_stats += f"• {bt['_id']}: {bt['count']}\n"
        
        # Statistiques abonnements
        subscriptions = {
            "trial": db.users.count_documents({"subscription_tier": "trial"}),
            "demarrage": db.users.count_documents({"subscription_tier": "demarrage"}),
            "croissance": db.users.count_documents({"subscription_tier": "croissance"}),
            "elite": db.users.count_documents({"subscription_tier": "elite"})
        }
        
        message = (
            "📊 **STATISTIQUES GÉNÉRALES**\n\n"
            f"👥 **Utilisateurs**\n"
            f"• Total : {total_users}\n"
            f"• Nouveaux aujourd'hui : {new_today}\n"
            f"• Onboarding complet : {completed_onboarding}\n\n"
            f"🏢 **Types de Commerce**\n"
            f"{business_stats}\n"
            f"💳 **Abonnements**\n"
            f"• Essais : {subscriptions['trial']}\n"
            f"• Démarrage : {subscriptions['demarrage']}\n"
            f"• Croissance : {subscriptions['croissance']}\n"
            f"• Elite : {subscriptions['elite']}\n"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
    
    async def show_promotions_menu(self, query):
        """Affiche le menu promotions"""
        active_promos = db.promotions.count_documents({"status": "active"})
        used_promos = db.promotions.count_documents({"status": "used"})
        
        keyboard = [
            [InlineKeyboardButton("🎯 Créer promotion globale", callback_data="promo_create_global")],
            [InlineKeyboardButton("👤 Créer promotion personnelle", callback_data="promo_create_personal")],
            [InlineKeyboardButton("📋 Promotions actives", callback_data="promos_active")],
            [InlineKeyboardButton("🔙 Retour", callback_data="back_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🎁 **GESTION PROMOTIONS**\n\n"
            f"• Promotions actives : {active_promos}\n"
            f"• Promotions utilisées : {used_promos}\n\n"
            "Choisissez une option :",
            reply_markup=reply_markup
        )
    
    async def show_main_menu(self, query):
        """Retourne au menu principal"""
        keyboard = [
            [InlineKeyboardButton("👥 Utilisateurs", callback_data="users")],
            [InlineKeyboardButton("💰 Paiements", callback_data="payments")],
            [InlineKeyboardButton("📊 Statistiques", callback_data="stats")],
            [InlineKeyboardButton("🎁 Promotions", callback_data="promotions")],
            [InlineKeyboardButton("📢 Message groupé", callback_data="broadcast")],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔧 **PANEL ADMIN COMMERCEBOOST**\n\n"
            "Choisissez une option :",
            reply_markup=reply_markup
        )
    
    # Commandes textuelles simples
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /stats pour avoir un rapide aperçu"""
        user_id = update.effective_user.id
        if user_id not in self.admin_users:
            return
        
        total_users = db.users.count_documents({})
        active_users = db.users.count_documents({"status": "active"})
        today_payments = db.payments.count_documents({
            "payment_date": {"$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        
        await update.message.reply_text(
            f"📈 **STATS RAPIDES**\n\n"
            f"👥 Utilisateurs totaux : {total_users}\n"
            f"✅ Utilisateurs actifs : {active_users}\n"
            f"💰 Paiements aujourd'hui : {today_payments}\n"
            f"🕐 Dernière mise à jour : {datetime.now().strftime('%H:%M')}"
        )
    
    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /users pour voir les derniers utilisateurs"""
        user_id = update.effective_user.id
        if user_id not in self.admin_users:
            return
        
        recent_users = list(db.users.find().sort("created_at", -1).limit(5))
        
        message = "👥 **5 DERNIERS UTILISATEURS**\n\n"
        for user in recent_users:
            created = user['created_at'].strftime('%d/%m/%Y')
            status = user.get('status', 'inactive')
            tier = user.get('subscription_tier', 'trial')
            business_type = user.get('business_type', 'N/A')
            message += f"• {user.get('name', 'N/A')} - {business_type} - {tier} - {status} - {created}\n"
        
        await update.message.reply_text(message)
    
    def setup_handlers(self, application):
        """Configure les handlers"""
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("users", self.users_command))
        application.add_handler(CallbackQueryHandler(self.button_handler))
    
    def start_bot(self):
        """Démarre le bot Telegram"""
        if not self.token:
            print("❌ Token Telegram non configuré")
            return
        
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers(self.application)
        
        print("🤖 Bot Telegram Admin démarré")
        self.application.run_polling()

# Instance globale
telegram_bot = TelegramAdminBot()