from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class FilmCountryBudgetAllocation(Base):
    __tablename__ = 'ric_film_country_budget_allocations'

    country_id = Column(Integer, ForeignKey('ric_countries.id'), primary_key=True)
    film_id = Column(Integer, ForeignKey('ric_films.id'), primary_key=True)
    budget_allocation = Column(Float, nullable=False)

    country = relationship("Country", back_populates="film_budget_allocations")
    film = relationship("Film", back_populates="country_budget_allocations")