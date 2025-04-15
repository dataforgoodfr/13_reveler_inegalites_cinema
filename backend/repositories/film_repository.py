from sqlalchemy import select, func
from sqlalchemy.orm import Session
from database.models import Film
from database.utils import matching

def create_film(session: Session, film_data: dict) -> Film:
    film = Film(**film_data)
    session.add(film)
    session.flush()
    return film

def get_or_create_film_by_similarity_pg_trgm(session: Session, new_name: str) -> Film:
    """
    Searches for an existing film using PostgreSQL's pg_trgm similarity function.
    If a similar film exists (similarity > 0.8), returns it.
    Otherwise, creates and returns a new film.
    """
    similarity_threshold = 0.8
    stmt = (
        select(Film)
        .where(func.similarity(
            func.unaccent(Film.original_name), func.unaccent(new_name)
        ) > similarity_threshold)
        .order_by(func.similarity(func.unaccent(Film.original_name), func.unaccent(new_name)).desc())
        .limit(1)
    )

    existing_film = session.execute(stmt).scalar_one_or_none()
    
    if existing_film:
        return existing_film

    data = { "original_name": new_name }
    film = create_film(session, data)
    return film

def find_or_create_film(session: Session, original_name: str) -> Film:
    film = session.query(Film).filter_by(original_name=original_name).first()
    if not film:
        data = { "original_name": original_name }
        film = create_film(session, data)
    return film

def find_film(session: Session, visa_number: str | int) -> Film | None:
    film = session.execute(
        select(Film).where(Film.visa_number == str(visa_number))
    ).first()
    return film
