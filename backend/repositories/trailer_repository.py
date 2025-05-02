from database.models import Trailer
from sqlalchemy.orm import Session

def create_or_update_trailer(session: Session, film_id, url):
    existing = session.query(Trailer).filter_by(film_id=film_id).first()
    if existing:
        existing.url = url
    else:
        new_trailer = Trailer(film_id=film_id, url=url)
        session.add(new_trailer)