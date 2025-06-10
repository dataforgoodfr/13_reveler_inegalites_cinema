from database.models import PosterCharacter
from sqlalchemy.orm import Session

def create_or_update_poster_character(session: Session, poster_id: int, data: dict):
    existing = session.query(PosterCharacter).filter_by(
        poster_id=poster_id,
        gender=data.get("gender"),
        age_min=data.get("age_min"),
        age_max=data.get("age_max"),
        ethnicity=data.get("ethnicity")
    ).first()

    if existing:
        existing.poster_percentage = data.get("poster_percentage")
    else:
        character = PosterCharacter(
            poster_id=poster_id,
            gender=data.get("gender"),
            age_min=data.get("age_min"),
            age_max=data.get("age_max"),
            ethnicity=data.get("ethnicity"),
            poster_percentage=data.get("poster_percentage"),
        )
        session.add(character)
        session.flush()
        return character.id

    session.flush()
    return existing.id
