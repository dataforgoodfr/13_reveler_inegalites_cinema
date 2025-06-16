from database.models import TrailerCharacter
from sqlalchemy.orm import Session

def delete_all_by_trailer_id(session: Session, trailer_id: int):
    session.query(TrailerCharacter).filter_by(trailer_id=trailer_id).delete()

def create_trailer_character(session: Session, trailer_id: int, data: dict):
    character = TrailerCharacter(
        trailer_id=trailer_id,
        gender=data.get("gender"),
        age_min=data.get("age_min"),
        age_max=data.get("age_max"),
        ethnicity=data.get("ethnicity"),
        time_on_screen=data.get("time_on_screen"),
        average_size_on_screen=data.get("average_size_on_screen")
    )
    session.add(character)
