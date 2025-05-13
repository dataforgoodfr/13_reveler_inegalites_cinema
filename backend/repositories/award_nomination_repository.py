from sqlalchemy.orm import Session
from sqlalchemy import extract
from database.models import AwardNomination, FestivalAward
from typing import List

def find_or_create_award_nomination(session: Session, film_id: int, award_id: int, is_winner: str, date: str) -> AwardNomination:
    nomination = session.query(AwardNomination).filter_by(film_id=film_id, award_id=award_id).first()
    if not nomination:
        data = {
            "film_id": film_id,
            "award_id": award_id,
            "is_winner": is_winner,
            "date": date
        }
        nomination = AwardNomination(**data)
        session.add(nomination)
        session.flush()
    return nomination

def get_award_nominations_by_award_id(session: Session, award_id: int) -> List[AwardNomination]:
    """
    Returns a list of nominations associated with a given festival award.
    """
    return session.query(AwardNomination).filter_by(award_id=award_id).all()

def get_years_with_awards(session: Session, festival_id: int) -> List[int]:
    """Get the list of years where the festival has at least one award."""
    # Fetch all years with at least one award or nomination
    years_with_awards = (
        session.query(extract('year', AwardNomination.date))
        .join(FestivalAward)
        .filter(FestivalAward.festival_id == festival_id)
        .distinct()
        .all()
    )
    return [int(year[0]) for year in years_with_awards]
