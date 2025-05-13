from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, extract, cast, String
from database.models import (
    AwardNomination,
    FestivalAward,
    FilmCredit,
    CreditHolder,
    Role,
)

def calculate_female_representation_in_nominated_films(session: Session, festival_id: int, year: str) -> float:
    """Calculates the percentage of nominated films with ≥1 female director in a specific year.
    """
    # Get nominated films for this festival/year
    nominated_films = (
        session.query(distinct(AwardNomination.film_id).label("film_id"))
        .join(FestivalAward, FestivalAward.id == AwardNomination.award_id)
        .filter(
            FestivalAward.festival_id == festival_id,
            cast(extract('year', AwardNomination.date), String) == year
        )
        .subquery()
    )

    total_films_count = session.query(func.count()).select_from(nominated_films).scalar()
    if not total_films_count:
        return 0.0
    
    female_directed_count = (
        session.query(distinct(FilmCredit.film_id))
        .join(CreditHolder, CreditHolder.id == FilmCredit.credit_holder_id)
        .join(Role, Role.id == FilmCredit.role_id)
        .filter(
            FilmCredit.film_id.in_(session.query(nominated_films.c.film_id)),
            Role.name == "director",
            CreditHolder.type == "Individual",
            func.lower(CreditHolder.gender) == "female"
        )
        .count()
    )

    return round(female_directed_count / total_films_count, 2) * 100

def calculate_female_representation_in_award_winning_films(session: Session, festival_id: int, year: str) -> float:
    """Calculates percentage of awards given to films with ≥1 female director in a specific year.
    """
    # Get all award wins for this festival/year
    award_wins = (
        session.query(AwardNomination.film_id)
        .join(FestivalAward, FestivalAward.id == AwardNomination.award_id)
        .filter(
            FestivalAward.festival_id == festival_id,
            AwardNomination.is_winner is True,
            cast(extract('year', AwardNomination.date), String) == year
        )
        .all()
    )
    
    if not award_wins:
        return 0.0
    
    winning_film_ids = {f[0] for f in award_wins}
    
    # Get films with female directors
    female_directed_films = (
        session.query(distinct(FilmCredit.film_id))
        .join(CreditHolder, CreditHolder.id == FilmCredit.credit_holder_id)
        .join(Role, Role.id == FilmCredit.role_id)
        .filter(
            FilmCredit.film_id.in_(winning_film_ids),
            Role.name == "director", 
            CreditHolder.type == "Individual",
            func.lower(CreditHolder.gender) == "female"
        )
        .all()
    )
    female_directed_ids = {f[0] for f in female_directed_films}
    
    # Count qualifying awards
    qualifying_awards = sum(1 for film_id, in award_wins if film_id in female_directed_ids)

    return round(qualifying_awards / len(award_wins), 2)  * 100