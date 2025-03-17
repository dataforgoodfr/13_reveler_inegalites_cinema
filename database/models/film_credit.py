from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class FilmCredit(Base):
    __tablename__ = "film_credits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    film_id = Column(Integer, ForeignKey("films.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    credit_holder_id = Column(Integer, ForeignKey("credit_holders.id"), nullable=False)

    film = relationship("Film", backref="film_credits")
    role = relationship("Role", backref="film_credits")
    credit_holder = relationship("CreditHolder", backref="film_credits")