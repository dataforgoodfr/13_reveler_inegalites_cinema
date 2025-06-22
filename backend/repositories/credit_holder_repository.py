from sqlalchemy.orm import Session
from database.models import FilmCredit, CreditHolder, AwardNomination, FestivalAward, Role
from backend.utils.name_utils import split_full_name, guess_gender, remove_extra_spaces
from backend.utils.date_utils import safe_year_to_date_range

def find_or_create_credit_holder(session: Session, full_name: str, type: str) -> CreditHolder:
    if not full_name or not type:
        raise ValueError("Both full_name and type are required to find or create a credit holder")
    
    full_name = remove_extra_spaces(full_name).lower()
    if type == 'Individual':
        first_name, last_name = split_full_name(full_name)
        gender = guess_gender(first_name.capitalize())
        filters = {
            'type': type,
            'first_name': first_name,
            'last_name': last_name,
            'gender': gender
        }
    elif type == 'Company':
        filters = {
            'type': type,
            'legal_name': full_name
        }
    else:
        raise ValueError("Invalid credit holder type")
    holder = session.query(CreditHolder).filter_by(**filters).first()
    if not holder:
        holder = CreditHolder(**filters)
        session.add(holder)
        session.flush()
    
    return holder

def find_directors_of_nominated_films_in_festival(session: Session, festival_id: int, festival_year: int) -> list[dict]:
    date_range = safe_year_to_date_range(festival_year)
    if not date_range:
        return []
    start_date, end_date = date_range

    results = (
        session.query(
            FilmCredit.film_id,
            CreditHolder.gender,
            AwardNomination.is_winner
        )
        .join(Role, Role.id == FilmCredit.role_id)
        .join(CreditHolder, CreditHolder.id == FilmCredit.credit_holder_id)
        .join(AwardNomination, AwardNomination.film_id == FilmCredit.film_id)
        .join(FestivalAward, FestivalAward.id == AwardNomination.award_id)
        .filter(
            FestivalAward.festival_id == festival_id,
            AwardNomination.date.between(start_date, end_date),
            Role.name == "director",
            CreditHolder.type == "Individual"
        )
        .all()
    )

    return [
        {
            "film_id": film_id,
            "director_gender": (gender or "").lower(),
            "film_is_winner": is_winner,
        }
        for film_id, gender, is_winner in results
    ]
