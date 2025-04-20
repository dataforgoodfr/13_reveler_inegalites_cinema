from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class PosterCharacter(Base):
    __tablename__ = 'ric_poster_characters'

    id = Column(Integer, primary_key=True)
    poster_id = Column(Integer, ForeignKey('ric_posters.id'), nullable=False)
    gender = Column(String, nullable=True)
    age_min = Column(Integer, nullable=True)
    age_max = Column(Integer, nullable=True)
    ethnicity = Column(String, nullable=True)
    poster_percentage = Column(Float, nullable=True)

    poster = relationship("Poster", back_populates="characters")
