from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models import Film

def create_film(session: Session, film_data: dict) -> Film:
    film = Film(**film_data)
    session.add(film)
    session.flush()
    return film

def find_or_create_film(session: Session, original_name: str) -> Film:
    film = session.query(Film).filter_by(original_name=original_name).first()
    if not film:
        data = { "original_name": original_name }
        film = create_film(session, data)
    return film

def find_film(session: Session, visa_number: str | int) -> Film | None:
    film = session.execute(
        select(Film).where(Film.visa_number == str(visa_number))
    ).first()
    return film
