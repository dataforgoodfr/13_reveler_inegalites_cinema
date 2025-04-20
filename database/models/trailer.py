from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Trailer(Base):
    __tablename__ = 'ric_trailers'

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    film_id = Column(Integer, ForeignKey('ric_films.id'), nullable=False)

    film = relationship("Film", back_populates="trailer")
    characters = relationship("TrailerCharacter", back_populates="trailer")
