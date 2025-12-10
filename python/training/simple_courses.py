# python/training/simple_courses.py
COURSES = {
    "debutant": [
        {"title": "Bases du commerce", "content": "Choisir secteur rentable au Togo..."}
        # Ajoute modules
    ],
    # ... intermédiaire, expérimenté
}

def get_course(level: str):
    return COURSES.get(level, [])