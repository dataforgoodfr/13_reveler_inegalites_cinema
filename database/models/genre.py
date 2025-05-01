from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class Genre(Base):
    __tablename__ = 'ric_genres'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    films = relationship('Film', secondary='ric_films_genres', back_populates='genres')