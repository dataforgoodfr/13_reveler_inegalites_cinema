from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, extract, cast, String, true
from database.models import (
    AwardNomination,
    FestivalAward,
    FilmCredit,
    CreditHolder,
    Role,
)

def get_film_ids(session, festival_id: int, year: str, is_winner: bool = False) -> set[int]:
    """Returns film IDs for nominations or wins at a specific festival and year."""
    query = (
        session.query(distinct(AwardNomination.film_id))
        .join(FestivalAward, FestivalAward.id == AwardNomination.award_id)
        .filter(
            FestivalAward.festival_id == festival_id,
            cast(extract('year', AwardNomination.date), String) == year
        )
    )
    if is_winner:
        query = query.filter(AwardNomination.is_winner.is_(true()))
    return {film_id for film_id, in query.all()}

def get_female_directed_film_ids(session, film_ids: set[int]) -> set[int]:
    """Returns film IDs that have at least one female director."""
    return {
        film_id for film_id, in session.query(distinct(FilmCredit.film_id))
        .join(CreditHolder, CreditHolder.id == FilmCredit.credit_holder_id)
        .join(Role, Role.id == FilmCredit.role_id)
        .filter(
            FilmCredit.film_id.in_(film_ids),
            Role.name == "director",
            CreditHolder.type == "Individual",
            func.lower(CreditHolder.gender) == "female"
        )
        .all()
    }

def calculate_female_representation_in_nominated_films(session, festival_id: int, year: str) -> float:
    """Calculates % of nominated films with ≥1 female director."""
    film_ids = get_film_ids(session, festival_id, year, is_winner=False)
    if not film_ids:
        return 0.0

    female_film_ids = get_female_directed_film_ids(session, film_ids)
    return round((len(female_film_ids) / len(film_ids)) * 100, 2)

def calculate_female_representation_in_award_winning_films(session, festival_id: int, year: str) -> float:
    """Calculates % of award-winning films with ≥1 female director."""
    film_ids = get_film_ids(session, festival_id, year, is_winner=True)
    if not film_ids:
        return 0.0

    female_film_ids = get_female_directed_film_ids(session, film_ids)
    return round((len(female_film_ids) / len(film_ids)) * 100, 2)
