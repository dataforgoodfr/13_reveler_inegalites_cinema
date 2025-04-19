from sqlalchemy.orm import Session
from database.models import Festival

def find_or_create_festival(session: Session, country_id: int, name: str, description: str, image_base64: str) -> Festival:
    festival = session.query(Festival).filter_by(
        name = name,
        country_id = country_id
        ).first()
    
    if not festival:
        data = {
            "name": name,
            "description": description,
            "image_base64": image_base64,
            "country_id": country_id,
        }
        festival = Festival(**data)
        session.add(festival)
        session.flush()

    return festival

def get_festival(session: Session, festival_id: int) -> Festival:
    festival = session.query(Festival).filter(Festival.id == festival_id).first()
    if not festival:
        return None
    return festival