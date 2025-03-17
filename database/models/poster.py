from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Poster(Base):
    __tablename__ = 'posters'

    id = Column(Integer, primary_key=True)
    image_base64 = Column(String, nullable=False)
    film_id = Column(Integer, ForeignKey('films.id'), nullable=False)

    film = relationship("Film", back_populates="poster")