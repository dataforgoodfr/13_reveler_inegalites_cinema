from sqlalchemy import select, func
from sqlalchemy.orm import Session
from database.models import Film, FilmCredit, Role, CreditHolder, AwardNomination
from backend.entities.credit_holder_entity import CreditHolderEntity
from typing import List
from backend.utils.name_utils import split_full_name

def create_film(session: Session, film_data: dict) -> Film:
    film = Film(**film_data)
    session.add(film)
    session.flush()
    return film

def find_most_similar_film_by_director(session: Session, film_title: str, director_full_name: str, threshold: float = 0.8) -> Film | None:
    first_name, last_name = split_full_name(director_full_name)

    stmt = (
        select(Film)
        .join(FilmCredit, FilmCredit.film_id == Film.id)
        .join(CreditHolder, CreditHolder.id == FilmCredit.credit_holder_id)
        .join(Role, Role.id == FilmCredit.role_id)
        .where(func.lower(Role.name) == "director")
        .where(
            func.unaccent(func.lower(CreditHolder.first_name)) == func.unaccent(func.lower(first_name)),
            func.unaccent(func.lower(CreditHolder.last_name)) == func.unaccent(func.lower(last_name))
        )
        .where(
            func.similarity(
                func.unaccent(Film.original_name),
                func.unaccent(film_title)
            ) > threshold
        )
        .order_by(
            func.similarity(func.unaccent(Film.original_name), func.unaccent(film_title)).desc()
        )
        .limit(1)
    )
    return session.execute(stmt).scalar_one_or_none()


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
