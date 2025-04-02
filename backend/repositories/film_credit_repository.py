from sqlalchemy.orm import Session
from database.models import FilmCredit

def create_film_credit(session: Session, film_id: int, role_id: int, credit_holder_id: int) -> FilmCredit:
    credit = FilmCredit(
        film_id=film_id,
        role_id=role_id,
        credit_holder_id=credit_holder_id
    )
    session.add(credit)
    return credit