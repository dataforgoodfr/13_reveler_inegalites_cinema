from sqlalchemy.orm import Session
from database.models import Festival, AwardNomination, FestivalAward
from typing import Dict, List

def get_festivals_by_film_id(session: Session, film_id: int) -> List[Dict]:
    results = (
        session.query(
            Festival.id,
            Festival.name,
            Festival.image_base64,
            AwardNomination.date
        )
        .join(FestivalAward, FestivalAward.festival_id == Festival.id)
        .join(AwardNomination, AwardNomination.award_id == FestivalAward.id)
        .filter(AwardNomination.film_id == film_id)
        .distinct(Festival.name)
        .all()
    )

    festivals = []
    for id, name, image_base64, date in results:
            festivals.append({
                "festival_id": id,
                "name": name,
                "year": date.year if date else None,
                "image_base64": image_base64
            })

    return festivals

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