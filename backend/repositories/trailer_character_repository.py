from database.models import Film, Trailer, TrailerCharacter
from sqlalchemy.orm import Session
from sqlalchemy import delete

def bulk_delete_by_film_visas(session, film_visas: list):
    """
    Deletes all TrailerCharacter records linked to trailers of films
    whose visa_number is in the given list.

    Args:
        session (Session): SQLAlchemy session
        film_visas (list): List of visa numbers to target
    """
    if not film_visas:
        return

    stmt = (
        delete(TrailerCharacter)
        .where(
            TrailerCharacter.trailer_id == Trailer.id,
            Trailer.film_id == Film.id,
            Film.visa_number.in_(film_visas)
        )
        .execution_options(synchronize_session=False)
    )
    session.execute(stmt)


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
