from sqlalchemy.orm import Session
from database.models import FestivalAward
from database.models import Festival

def get_festival_award_by_name(session: Session, festival_name: str, award_name: str):
    """
     Get festival award by name and join with festival name
    """
    festival = session.query(FestivalAward).join(
        Festival, FestivalAward.festival_id == Festival.id
    ).filter(
        FestivalAward.name == award_name,
        Festival.name == festival_name
    ).all()

    return festival

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
    