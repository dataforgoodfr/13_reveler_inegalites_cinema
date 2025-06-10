from database.models import TrailerCharacter
from sqlalchemy.orm import Session

def create_or_update_trailer_character(session: Session, trailer_id: int, data: dict):
    existing = session.query(TrailerCharacter).filter_by(
        trailer_id=trailer_id,
        gender=data.get("gender"),
        age_min=data.get("age_min"),
        age_max=data.get("age_max"),
        ethnicity=data.get("ethnicity")
    ).first()

    if existing:
        existing.time_on_screen = data.get("time_on_screen")
        existing.average_size_on_screen = data.get("average_size_on_screen")
    else:
        character = TrailerCharacter(
            trailer_id=trailer_id,
            gender=data.get("gender"),
            age_min=data.get("age_min"),
            age_max=data.get("age_max"),
            ethnicity=data.get("ethnicity"),
            time_on_screen=data.get("time_on_screen"),
            average_size_on_screen=data.get("average_size_on_screen"),
        )
        session.add(character)
        session.flush()  # pour avoir character.id si nécessaire
        return character.id  # renvoyer l'id nouvellement créé

    session.flush()
    return existing.id  # renvoyer l'id existant
