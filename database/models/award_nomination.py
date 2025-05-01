from sqlalchemy import Column, Integer, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from database.database import Base

class AwardNomination(Base):
    __tablename__ = "ric_award_nominations"

    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey("ric_films.id"), nullable=False)
    credit_holder_id = Column(Integer, ForeignKey("ric_credit_holders.id"))
    award_id = Column(Integer, ForeignKey("ric_festival_awards.id"), nullable=False)
    date = Column(Date, nullable=False)
    is_winner = Column(Boolean, default=False, nullable=False)

    film = relationship("Film", back_populates="award_nominations")
    credit_holder = relationship("CreditHolder", back_populates="award_nominations")
    festival_award = relationship("FestivalAward", back_populates="award_nominations")
