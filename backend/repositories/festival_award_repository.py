from sqlalchemy.orm import Session
from database.models import FestivalAward
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