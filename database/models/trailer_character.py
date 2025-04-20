from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class TrailerCharacter(Base):
    __tablename__ = 'ric_trailer_characters'

    id = Column(Integer, primary_key=True)
    trailer_id = Column(Integer, ForeignKey('ric_trailers.id'), nullable=False)
    gender = Column(String, nullable=True)
    age_min = Column(Integer, nullable=True)
    age_max = Column(Integer, nullable=True)
    ethnicity = Column(String, nullable=True)
    time_on_screen = Column(Float, nullable=True)
    average_size_on_screen = Column(Float, nullable=True)

    trailer = relationship("Trailer", back_populates="characters")
