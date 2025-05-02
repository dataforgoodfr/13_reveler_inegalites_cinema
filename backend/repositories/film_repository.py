from sqlalchemy import select, func
from sqlalchemy.orm import Session
from database.models import Film, FilmCredit, Role, CreditHolder, AwardNomination
from backend.entities.credit_holder_entity import CreditHolderEntity
from typing import List

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

def find_film_by_visa(session: Session, visa_number: str | int) -> Film | None:
    return session.query(Film).filter_by(visa_number=str(visa_number)).first()

def get_individual_directors_for_film(session: Session, film_id: int) -> list[str]:
    # Fetch the 'director' role
    director_role = session.scalar(
        select(Role).where(func.lower(Role.name) == "director")
    )
    if not director_role:
        return []

    # Get all individual director credit holders for this film
    stmt = (
        select(CreditHolder)
        .join(FilmCredit, FilmCredit.credit_holder_id == CreditHolder.id)
        .where(
            FilmCredit.film_id == film_id,
            FilmCredit.role_id == director_role.id,
            CreditHolder.type == "Individual"
        )
    )

    results = session.scalars(stmt).all()

    return [CreditHolderEntity(holder).full_name() for holder in results]

def get_films_by_award_id(session: Session, award_id: int) -> List[Film]:
    """
    Returns a list of films that were nominated for a specific award.
    """
    return (
        session.query(Film)
        .join(AwardNomination, AwardNomination.film_id == Film.id)
        .filter(AwardNomination.award_id == award_id)
        .all()
    )