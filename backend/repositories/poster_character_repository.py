from database.models import PosterCharacter
from sqlalchemy.orm import Session

def delete_all_by_poster_id(session: Session, poster_id: int):
    session.query(PosterCharacter).filter_by(poster_id=poster_id).delete()

def create_poster_character(session: Session, poster_id: int, data: dict):
    character = PosterCharacter(
        poster_id=poster_id,
        gender=data.get("gender"),
        age_min=data.get("age_min"),
        age_max=data.get("age_max"),
        ethnicity=data.get("ethnicity"),
        poster_percentage=data.get("poster_percentage")
    )
    session.add(character)
