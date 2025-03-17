from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class Country(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    film_budget_allocations = relationship("FilmCountryBudgetAllocation", back_populates="country")
    films = relationship('Film', secondary='film_country_budget_allocations', back_populates='countries')
    festivals = relationship("Festival", backref="country")
