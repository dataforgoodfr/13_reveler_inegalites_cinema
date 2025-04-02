from sqlalchemy.orm import Session
from database.models import Role

def find_or_create_role(session: Session, name: str) -> Role:
    role = session.query(Role).filter_by(name=name).first()
    if not role:
        role = Role(name=name)
        session.add(role)
        session.flush()
    return role