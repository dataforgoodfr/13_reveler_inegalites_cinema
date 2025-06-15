from sqlalchemy import Column, Integer, String, Date, Float, Boolean, Index
from sqlalchemy.orm import relationship
from database.database import Base

class Film(Base):
    __tablename__ = "ric_films"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_name = Column(String, nullable=False)
    visa_number = Column(String, nullable=True)
    release_date = Column(Date, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    budget = Column(Float, nullable=True)
    parity_bonus = Column(Boolean, nullable=True, default=False)
    eof = Column(Boolean, nullable=True, default=False)
    asr = Column(String, nullable=True)
    sofica_funding = Column(Boolean, nullable=True, default=False)
    tax_credit = Column(Boolean, nullable=True, default=False)
    regional_funding = Column(Boolean, nullable=True, default=False)
    cnc_agrement_year = Column(Integer, nullable=True)
    cnc_rank = Column(Integer, nullable=True)
    allocine_id = Column(Integer, nullable=True)
    mubi_id = Column(Integer, nullable=True)

    genres = relationship('Genre', secondary='ric_films_genres', back_populates='films')
    country_budget_allocations = relationship("FilmCountryBudgetAllocation", back_populates="film")
    trailer = relationship("Trailer", back_populates="film")
    poster = relationship("Poster", back_populates="film")
    film_credits = relationship("FilmCredit", back_populates="film")
    award_nominations = relationship("AwardNomination", back_populates="film")

    # Add index on original_name
    __table_args__ = (
        Index(
            "film_original_name_trgm_idx",
            original_name,
            postgresql_using="gin",
            postgresql_ops={"original_name": "gin_trgm_ops"},
        ),
    )
