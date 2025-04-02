from sqlalchemy.orm import Session
from database.models import Country

def find_or_create_country(session: Session, country_name: str) -> Country:
    country = session.query(Country).filter_by(name=country_name).first()
    if not country:
        country = Country(name=country_name)
        session.add(country)
        session.flush()
    return country
