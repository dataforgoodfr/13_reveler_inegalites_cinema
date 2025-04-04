from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database.database import Base

class Role(Base):
    __tablename__ = 'ric_roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_key_role = Column(Boolean, default=False, nullable=False)

    film_credits = relationship("FilmCredit", back_populates="role")
