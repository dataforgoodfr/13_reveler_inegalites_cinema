from database.models import Genre
from sqlalchemy.orm import Session
from backend.utils.name_utils import remove_extra_spaces

def find_or_create_genre(session: Session, name: str) -> Genre:
    if not name:
        raise ValueError("You must provide a genre name")
    name = remove_extra_spaces(name).lower()
    
    genre = session.query(Genre).filter(Genre.name == name).first()
    if not genre:
        genre = Genre(name=name)
        session.add(genre)
        session.flush()
    return genre
