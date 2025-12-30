# python/content_manager.py
from datetime import datetime, timedelta
from random import choice

# Conseils prédéfinis (tu ajoutes/supprimes à la main)
CONSEILS_QUOTIDIENS = [
    "Augmente ce produit de 100 FCFA, tes clients ne diront rien.",
    "Arrête les promos sur les produits à faible marge.",
    "Mets en avant tes produits moyens, ils se vendent plus vite.",
    "N'affiche pas trop de choix, le client hésite et part.",
    "Propose un petit cadeau pour tout achat au-dessus d’un certain montant."
]

def calculer_marge(achat, frais, vente_actuel):
    cout_total = achat + frais
    if vente_actuel <= cout_total:
        return {
            "marge": 0,
            "alerte": "Tu vends à perte ! Augmente ton prix.",
            "prix_conseille": int(cout_total * 1.3)  # 30% marge cible
        }
    marge_percent = round((vente_actuel - cout_total) / vente_actuel * 100, 1)
    prix_conseille = int(cout_total * 1.3) if marge_percent < 25 else vente_actuel
    return {
        "marge": marge_percent,
        "alerte": None if marge_percent > 20 else "Marge faible, tu peux augmenter.",
        "prix_conseille": prix_conseille
    }

def generer_conseil_quotidien():
    return choice(CONSEILS_QUOTIDIENS)

def generer_promo(type_promo):
    templates = {
        "jour": "Promo du jour : Achetez 2, le 3e à moitié prix ! Partage sur WhatsApp",
        "weekend": "Week-end spécial : Tout à -20% samedi et dimanche ! Venez nombreux",
        "destockage": "Déstocage massif : Prix cassés sur tout le stock ancien ! Premier arrivé, premier servi"
    }
    return templates.get(type_promo, "Promo spéciale aujourd'hui ! Viens découvrir en boutique.")