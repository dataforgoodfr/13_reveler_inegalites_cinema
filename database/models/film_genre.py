from sqlalchemy import Column, Integer, ForeignKey
from database.database import Base

class FilmGenre(Base):
    __tablename__ = 'films_genres'

    film_id = Column(Integer, ForeignKey('films.id'), primary_key=True)
    genre_id = Column(Integer, ForeignKey('genres.id'), primary_key=True)
