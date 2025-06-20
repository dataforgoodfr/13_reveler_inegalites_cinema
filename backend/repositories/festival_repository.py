from sqlalchemy.orm import Session
from database.models import Festival
from backend.constants.festival_constants import FESTIVALS
from backend.repositories import country_repository

def find_or_create_festival(session: Session, name: str) -> Festival:
    festival_data = next((f for f in FESTIVALS if f['name'].lower() == name.lower()), None)
    if not festival_data:
        return None

    festival = session.query(Festival).filter_by(name = name).first()
    
    if not festival:
        country_name = festival_data.get("country", "Unknown")
        country = country_repository.find_or_create_country(session, country_name)
        data = {
            "name": name,
            "description": festival_data.get("description", ""),
            "image_base64": festival_data.get("image_url", ""),
            "country_id": country.id,
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
