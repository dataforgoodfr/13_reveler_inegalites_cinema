from sqlalchemy.orm import Session
from sqlalchemy import extract
from database.models import FestivalAward, AwardNomination
from typing import List

def insert_festival_award(session: Session, name: str, festival_id: int) -> FestivalAward:
    festival_award = session.query(FestivalAward).filter_by(name=name).first()

    if not festival_award:
        data = {
            "name": name,
            "festival_id": festival_id,
        }
        festival_award = FestivalAward(**data)
        session.add(festival_award)
        session.flush()
    return festival_award
    
def get_festival_awards_by_festival_id(session: Session, festival_id: int) -> List[FestivalAward]:
    """
    Returns a list of awards associated with a given festival.
    """
    return session.query(FestivalAward).filter_by(festival_id=festival_id).all()


def get_festival_awards_by_id_year(session: Session, festival_id: int, year: int) -> List[FestivalAward]:
    """
    Returns a list of awards associated with a given festival and a given year.
    Only includes awards that have at least one nomination in the specified year.
    """
    subquery = (
        session.query(AwardNomination.award_id)
        .filter(extract('year', AwardNomination.date) == year)
        .subquery()
    )

    awards = (
        session.query(FestivalAward)
        .filter(
            FestivalAward.festival_id == festival_id,
            FestivalAward.id.in_(session.query(subquery))
        )
        .order_by(FestivalAward.name)
        .all()
    )

    return awards