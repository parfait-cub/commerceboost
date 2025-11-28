# Contenu pré-défini pour peupler la base de données

PREDEFINED_TIPS = [
    # === CONSEILS PHYSIQUE ===
    {
        "secteur": "general",
        "type_commerce": "physique",
        "conseil": "Gardez votre vitrine propre et attrayante. C'est votre première chance de faire bonne impression !",
        "tags": ["presentation", "physique"],
        "niveau": "debutant"
    },
    {
        "secteur": "general",
        "type_commerce": "physique", 
        "conseil": "Formez votre personnel à accueillir chaleureusement chaque client. Un bon service fait revenir les clients.",
        "tags": ["service", "physique"],
        "niveau": "intermediaire"
    },
    {
        "secteur": "general",
        "type_commerce": "physique",
        "conseil": "Organisez votre espace de vente pour créer un parcours client fluide et mettre en valeur vos meilleurs produits.",
        "tags": ["organisation", "physique"],
        "niveau": "intermediaire"
    },
    {
        "secteur": "alimentaire",
        "type_commerce": "physique",
        "conseil": "Placez les produits frais et odorants près de l'entrée. L'odorat influence beaucoup les décisions d'achat alimentaire.",
        "tags": ["presentation", "alimentaire", "physique"],
        "niveau": "debutant"
    },
    {
        "secteur": "mode",
        "type_commerce": "physique",
        "conseil": "Créez des tenues complètes sur mannequins. Les clients achètent plus facilement une tenue qu'un vêtement seul.",
        "tags": ["presentation", "mode", "physique"],
        "niveau": "intermediaire"
    },

    # === CONSEILS EN LIGNE ===
    {
        "secteur": "general",
        "type_commerce": "en_ligne",
        "conseil": "Prenez des photos professionnelles de vos produits sous plusieurs angles. La qualité des images booste les ventes en ligne.",
        "tags": ["digital", "presentation", "en_ligne"],
        "niveau": "debutant"
    },
    {
        "secteur": "general",
        "type_commerce": "en_ligne",
        "conseil": "Répondez rapidement aux messages des clients (moins de 2 heures). La réactivité build la confiance en ligne.",
        "tags": ["service", "digital", "en_ligne"],
        "niveau": "intermediaire"
    },
    {
        "secteur": "general",
        "type_commerce": "en_ligne",
        "conseil": "Utilisez WhatsApp Business pour communiquer avec vos clients. C'est le canal préféré des togolais pour le commerce.",
        "tags": ["communication", "digital", "en_ligne"],
        "niveau": "debutant"
    },
    {
        "secteur": "mode",
        "type_commerce": "en_ligne",
        "conseil": "Montrez vos vêtements portés par des modèles de différentes tailles. Aide les clients à mieux visualiser.",
        "tags": ["presentation", "mode", "en_ligne"],
        "niveau": "intermediaire"
    },
    {
        "secteur": "alimentaire",
        "type_commerce": "en_ligne",
        "conseil": "Proposez la livraison dans des créneaux horaires précis. Les clients apprécient savoir quand recevoir leurs produits frais.",
        "tags": ["service", "alimentaire", "en_ligne"],
        "niveau": "intermediaire"
    },

    # === CONSEILS MIXTES (LES DEUX) ===
    {
        "secteur": "general",
        "type_commerce": "mixte",
        "conseil": "Créez une carte de fidélité valable en ligne et en boutique. Fidélisez vos clients quel que soit leur canal d'achat.",
        "tags": ["fidelisation", "mixte"],
        "niveau": "intermediaire"
    },
    {
        "secteur": "general",
        "type_commerce": "mixte",
        "conseil": "Annoncez vos promotions à la fois en boutique et sur vos réseaux sociaux. Doublez votre visibilité !",
        "tags": ["promotion", "mixte"],
        "niveau": "debutant"
    },
    {
        "secteur": "general",
        "type_commerce": "mixte",
        "conseil": "Proposez 'click and collect' : commande en ligne, retrait en boutique. Combine les avantages des deux canaux.",
        "tags": ["innovation", "mixte"],
        "niveau": "experimente"
    },
    {
        "secteur": "mode",
        "type_commerce": "mixte",
        "conseil": "Autorisez le retour en boutique des articles achetés en ligne. Améliorez l'expérience client multicanale.",
        "tags": ["service", "mode", "mixte"],
        "niveau": "intermediaire"
    },

    # === CONSEILS GÉNÉRAUX ===
    {
        "secteur": "general",
        "type_commerce": "all",
        "conseil": "Notez les préférences de vos clients réguliers. La personnalisation fait la différence !",
        "tags": ["fidelisation", "service"],
        "niveau": "all"
    },
    {
        "secteur": "general",
        "type_commerce": "all",
        "conseil": "Faites un inventaire régulier pour éviter les ruptures de stock. Un produit manquant = une vente perdue.",
        "tags": ["gestion", "stock"],
        "niveau": "intermediaire"
    },
    {
        "secteur": "general",
        "type_commerce": "all",
        "conseil": "Proposez plusieurs moyens de paiement (Flooz, TMoney, cash). Facilitez l'achat pour vos clients.",
        "tags": ["service", "vente"],
        "niveau": "debutant"
    }
]

PREDEFINED_PROMOS = [
    # Promos pour commerce physique
    {
        "type": "stock_lent",
        "secteur": "general",
        "type_commerce": "physique",
        "titre": "Coin Soldes Physique",
        "description": "Créez un espace dédié aux articles en soldes avec signalétique claire",
        "avantage": "Écoulez les stocks lent en attirant les chasseurs de bonnes affaires",
        "exemple": "Zone '--50%' bien visible dans votre boutique"
    },
    {
        "type": "nouveaux_clients",
        "secteur": "general", 
        "type_commerce": "physique",
        "titre": "Première Visite Boutique",
        "description": "Offre de bienvenue pour les nouveaux clients en magasin",
        "avantage": "Convertit les nouveaux visiteurs en clients fidèles",
        "exemple": "Cadeau surprise ou -15% sur le premier achat"
    },

    # Promos pour commerce en ligne
    {
        "type": "stock_lent",
        "secteur": "general",
        "type_commerce": "en_ligne", 
        "titre": "Flash Sale Digital",
        "description": "Vente flash limitée dans le temps sur vos réseaux sociaux",
        "avantage": "Crée de l'urgence et booste le trafic sur votre page",
        "exemple": "Promo de 4 heures annoncée sur WhatsApp et Facebook"
    },
    {
        "type": "nouveaux_clients",
        "secteur": "general",
        "type_commerce": "en_ligne",
        "titre": "Code de Bienvenue Online",
        "description": "Code promo spécial pour les premiers achats en ligne",
        "avantage": "Incite à la première commande digitale",
        "exemple": "Code BIENVENUE10 pour -10% sur la première commande"
    },

    # Promos mixtes
    {
        "type": "fidelisation",
        "secteur": "general",
        "type_commerce": "mixte",
        "titre": "Carte Fidélité Multi-Canal",
        "description": "Système de points valable en ligne et en boutique",
        "avantage": "Fidélise les clients sur tous les canaux",
        "exemple": "1 point par 1000 FCFA, cumulable en ligne et en boutique"
    },
    {
        "type": "lancement",
        "secteur": "general",
        "type_commerce": "mixte",
        "titre": "Lancement Cross-Canal",
        "description": "Promo de lancement disponible sur tous les canaux",
        "avantage": "Maximise la visibilité des nouveaux produits",
        "exemple": "Prix spécial annoncé en boutique et sur les réseaux"
    }
]

INSPIRATIONAL_STORIES = [
    {
        "personnage": "Maman Afi",
        "secteur": "alimentaire",
        "type_commerce": "physique",
        "ville": "Lomé", 
        "histoire": "A commencé avec un petit étal de plats cuisinés devant sa maison. Grâce à la qualité constante et aux recommandations, elle a ouvert une petite boutique qui emploie maintenant 3 personnes.",
        "lecon": "La régularité dans la qualité transforme un petit commerce en entreprise viable"
    },
    {
        "personnage": "Jeanne Digital",
        "secteur": "mode",
        "type_commerce": "en_ligne",
        "ville": "Lomé",
        "histoire": "Elle a commencé à vendre des pagnes sur Instagram depuis son salon. Aujourd'hui, elle a un site web et livre dans tout le Togo grâce à des partenariats avec des transporteurs.",
        "lecon": "Les réseaux sociaux peuvent transformer une passion en business viable sans local physique"
    },
    {
        "personnage": "Papa Koffi",
        "secteur": "electronique", 
        "type_commerce": "mixte",
        "ville": "Kara",
        "histoire": "Il avait une petite boutique de recharge. Il a ajouté une page Facebook pour montrer ses accessoires. Maintenant, 40% de ses ventes viennent des commandes en ligne avec retrait en boutique.",
        "lecon": "Combiner physique et digital maximise votre potentiel de vente"
    }
]

MOTIVATION_MESSAGES = [
    {"message": "Chaque client satisfait est un ambassadeur potentiel, peu importe que vous vendiez en boutique ou en ligne ! 🌟"},
    {"message": "Votre commerce est unique. Que vous soyez en physique, en ligne ou les deux, croyez en votre valeur ! 💎"},
    {"message": "La persévérance paye, que vous accueilliez des clients en boutique ou que vous répondiez à des messages en ligne 🚀"},
    {"message": "Aujourd'hui est une nouvelle opportunité pour impressionner vos clients, peu importe comment ils vous contactent ! 🌈"},
    {"message": "Votre adaptabilité est votre force. Physique, en ligne ou mixte, vous créez votre succès ! 📈"}
]