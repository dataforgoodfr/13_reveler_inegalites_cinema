from sqlalchemy import Column, Integer, String, Enum, Date
from sqlalchemy.orm import relationship
from database.database import Base

class CreditHolder(Base):
    __tablename__ = "credit_holders"

    id = Column(Integer, primary_key=True)
    type = Column(Enum("Company", "Individual", name="credit_holder_type"), nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    legal_name = Column(String)  # Only for companies
    gender = Column(String)
    birthdate = Column(Date)

    film_credits = relationship("FilmCredit", back_populates="credit_holder")
