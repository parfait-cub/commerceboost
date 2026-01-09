import random

CONSEILS_QUOTIDIENS = [
    "Vérifie toujours ta marge avant de fixer un prix.",
    "Un client fidèle rapporte plus qu’un nouveau client.",
    "Note tes ventes chaque jour, même approximativement.",
]

PROMO_TEMPLATES = {
    "general": [
        "🔥 Promo du jour ! Achetez maintenant et économisez.",
        "🎁 Offre spéciale aujourd’hui seulement !",
    ]
}


def calcul_marge(prix_achat, charges, prix_vente):
    try:
        marge = prix_vente - (prix_achat + charges)
        taux = (marge / prix_vente) * 100 if prix_vente else 0
        return {
            "marge": round(marge, 2),
            "taux": round(taux, 2),
            "rentable": marge > 0
        }
    except Exception:
        return None


def conseil_aleatoire():
    return random.choice(CONSEILS_QUOTIDIENS)


def generer_promo(type_promo="general"):
    promos = PROMO_TEMPLATES.get(type_promo, PROMO_TEMPLATES["general"])
    return random.choice(promos)


# ⚠️ V1 : ajouts en mémoire uniquement (NON persistants)
def ajouter_conseil(conseil):
    CONSEILS_QUOTIDIENS.append(conseil)


def ajouter_promo(type_promo, message):
    PROMO_TEMPLATES.setdefault(type_promo, []).append(message)
