from sqlalchemy.orm import Session
from database.models import AwardNomination

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
