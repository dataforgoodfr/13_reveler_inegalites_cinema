from sqlalchemy import Column, Integer, String, Date, Float, Boolean
from sqlalchemy.orm import relationship
from database.database import Base

class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_name = Column(String, nullable=False)
    release_date = Column(Date, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    first_language = Column(String, nullable=True)
    tmdb_id = Column(Integer, nullable=True)
    budget = Column(Float, nullable=True)
    bechdel_compliant = Column(Boolean, nullable=True, default=False)
    parity_bonus = Column(Boolean, nullable=True, default=False)
    eof = Column(Boolean, nullable=True, default=False)
    asr = Column(Boolean, nullable=True, default=False)
    sofica_funding = Column(Boolean, nullable=True, default=False)
    tax_credit = Column(Boolean, nullable=True, default=False)
    regional_funding = Column(Boolean, nullable=True, default=False)
    cnc_agrement_year = Column(Date, nullable=True)
    cnc_rank = Column(Integer, nullable=True)

    genres = relationship('Genre', secondary='films_genres', back_populates='films')
    country_budget_allocations = relationship("FilmCountryBudgetAllocation", back_populates="film")
    countries = relationship('Country', secondary='film_country_budget_allocations', back_populates='films')
    trailer = relationship("Trailer", back_populates="film")
    poster = relationship("Poster", back_populates="film")
    film_credits = relationship("FilmCredit", back_populates="film")
