from sqlalchemy.orm import Session
from database.models import Film

def create_film(session: Session, film_data: dict) -> Film:
    film = Film(**film_data)
    session.add(film)
    session.flush()
    return film
