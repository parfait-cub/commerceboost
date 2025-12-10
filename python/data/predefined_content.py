# python/data/predefined_content.py
import random

HISTOIRES = [
    {"content": "Amina a commencé avec un petit stand à Lomé et a grandi grâce à la persévérance..."},
    # +10 histoires
]

PROMOTIONS = {
    "alimentation": "Promo {saison} : Achetez 2, 1 gratuit !"
    # + secteurs
}

def get_random_histoire():
    return random.choice(HISTOIRES)

def generate_promo(sector: str, saison: str):
    return PROMOTIONS.get(sector, "Promo générique").format(saison=saison)