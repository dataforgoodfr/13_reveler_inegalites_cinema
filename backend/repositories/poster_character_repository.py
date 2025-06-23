from database.models import Film, Poster, PosterCharacter
from sqlalchemy.orm import Session
from sqlalchemy import delete

def bulk_delete_by_film_visas(session, film_visas: list):
    """
    Deletes all PosterCharacter records linked to posters of films
    whose visa_number is in the given list.

    Args:
        session (Session): SQLAlchemy session
        film_visas (list): List of visa numbers to target
    """
    if not film_visas:
        return

    stmt = (
        delete(PosterCharacter)
        .where(
            PosterCharacter.poster_id == Poster.id,
            Poster.film_id == Film.id,
            Film.visa_number.in_(film_visas)
        )
        .execution_options(synchronize_session=False)
    )
    session.execute(stmt)

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
