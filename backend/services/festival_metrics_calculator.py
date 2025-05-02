from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import (
    AwardNomination,
    FestivalAward,
    FilmCredit,
    CreditHolder,
    Role,
)

def calculate_female_representation_in_nominated_films(session: Session, festival_id: int) -> float | None:
    # Get all nominated film IDs for this festival
    nominated_film_ids = (
        session.query(AwardNomination.film_id)
        .join(FestivalAward, FestivalAward.id == AwardNomination.award_id)
        .filter(FestivalAward.festival_id == festival_id)
        .distinct()
        .subquery()
    )
    
    # Query for nominated films, individual directors genders
    individual_representation = (
        session.query(CreditHolder.gender)
        .join(FilmCredit, FilmCredit.credit_holder_id == CreditHolder.id)
        .join(Role, Role.id == FilmCredit.role_id)
        .filter(
            FilmCredit.film_id.in_(nominated_film_ids),
            Role.name == "director",
            CreditHolder.type == "Individual"
        )
        .all()
    )

    total_representation = len(individual_representation)

    # Avoid division by zero
    if total_representation == 0:
        return 0.0

    female_directors = sum(1 for (gender,) in individual_representation if gender and gender.lower() == "female")

    return round(female_directors / total_representation, 2)

def calculate_female_representation_in_winner_price(session: Session, festival_id: int) -> float | None :
    # Get all the winned awards film IDs for a festival
    film_id_winned_awards = (
        session.query(AwardNomination.film_id)
        .join(FestivalAward, FestivalAward.id == AwardNomination.award_id)
        .filter(
            FestivalAward.festival_id == festival_id,
            AwardNomination.is_winner == True,
        )
        .subquery()
    )

    # Query for winned awards films, individual directors genders
    individual_representation = (
        session.query(CreditHolder.gender)
        .join(FilmCredit)
        .join(Role)
        .filter(
            FilmCredit.film_id.in_(film_id_winned_awards),
            Role.name == "director",
            CreditHolder.type == "Individual"
        )
        .all()
    )
    print(individual_representation)
    total_representation = len(individual_representation)

    # Avoid division by zero
    if total_representation == 0:
        return 0.0

    female_directors = sum(1 for (gender,) in individual_representation if gender and gender.lower() == "female")
    print("female_directors", female_directors)
    print("total_representation", total_representation)

    return round(female_directors / total_representation, 2)    