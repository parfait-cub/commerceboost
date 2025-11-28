from data.database import db
from datetime import datetime

class MarginCalculator:
    def calculate_margin(self, user_id, prix_achat, prix_vente):
        """Calcule la marge et sauvegarde le calcul"""
        try:
            prix_achat = float(prix_achat)
            prix_vente = float(prix_vente)
            
            marge_brute = prix_vente - prix_achat
            pourcentage_marge = (marge_brute / prix_achat) * 100 if prix_achat > 0 else 0
            
            conseil = self._generer_conseil_marge(pourcentage_marge)
            
            # Sauvegarde du calcul
            calcul_data = {
                "user_id": user_id,
                "prix_achat": prix_achat,
                "prix_vente": prix_vente,
                "marge_brute": marge_brute,
                "pourcentage_marge": round(pourcentage_marge, 2),
                "conseil": conseil,
                "timestamp": datetime.now()
            }
            
            db.margin_calculations.insert_one(calcul_data)
            
            return calcul_data
            
        except (ValueError, TypeError):
            return {"error": "Veuillez entrer des nombres valides"}
    
    def _generer_conseil_marge(self, marge):
        """Génère un conseil basé sur le pourcentage de marge"""
        if marge < 0:
            return "⚠️ Vous vendez à perte ! Revoyez rapidement vos prix."
        elif marge < 15:
            return "💡 Marge faible : Pensez à négocier vos prix d'achat ou à augmenter légèrement vos prix de vente"
        elif marge < 30:
            return "📊 Marge correcte : Vous pourriez tester des ventes groupées pour l'augmenter"
        elif marge < 50:
            return "✅ Bonne marge ! Continuez ainsi et surveillez la concurrence"
        else:
            return "🎉 Excellente marge ! Assurez-vous de rester compétitif par rapport au marché"
    
    def get_user_margin_history(self, user_id, limit=5):
        """Retourne l'historique des calculs de marge d'un utilisateur"""
        return list(db.margin_calculations.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit))

# Instance globale
margin_calculator = MarginCalculator()