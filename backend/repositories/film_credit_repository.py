from sqlalchemy.orm import Session
from database.models import FilmCredit

def find_or_create_film_credit(session: Session, film_id: int, role_id: int, credit_holder_id: int) -> FilmCredit:
    credit = session.query(FilmCredit).filter_by(
        film_id=film_id,
        role_id=role_id,
        credit_holder_id=credit_holder_id
    ).first()

    if credit:
        return credit  # Already exists, nothing to update for now

    # Create new credit
    credit = FilmCredit(
        film_id=film_id,
        role_id=role_id,
        credit_holder_id=credit_holder_id
    )
    session.add(credit)
    session.flush()  # optional if you need credit.id right away
    return credit
