from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class FestivalAward(Base):
    __tablename__ = "ric_festival_awards"

    id = Column(Integer, primary_key=True)
    mubi_label = Column(String, nullable=False)
    english_label = Column(String, nullable=True)
    french_label = Column(String, nullable=True)
    festival_id = Column(Integer, ForeignKey("ric_festivals.id"), nullable=False)

    festival = relationship("Festival", back_populates="awards")
    award_nominations = relationship("AwardNomination", back_populates="festival_award")