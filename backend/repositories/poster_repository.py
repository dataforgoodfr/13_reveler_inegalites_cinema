from database.models import Poster
from sqlalchemy.orm import Session

def create_or_update_poster(session: Session, film_id, image_base64):
    existing = session.query(Poster).filter_by(film_id=film_id).first()
    if existing:
        existing.image_base64 = image_base64
    else:
        new_poster = Poster(film_id=film_id, image_base64=image_base64)
        session.add(new_poster)