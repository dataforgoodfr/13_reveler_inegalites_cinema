from sqlalchemy import Column, Integer, ForeignKey
from database.database import Base

class FilmGenre(Base):
    __tablename__ = 'ric_films_genres'

    film_id = Column(Integer, ForeignKey('ric_films.id'), primary_key=True)
    genre_id = Column(Integer, ForeignKey('ric_genres.id'), primary_key=True)
