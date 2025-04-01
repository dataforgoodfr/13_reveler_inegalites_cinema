from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class FestivalAward(Base):
    __tablename__ = "festival_awards"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=False)

    festival = relationship("Festival", back_populates="awards")
    award_nominations = relationship("AwardNomination", back_populates="festival_award")