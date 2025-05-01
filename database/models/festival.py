from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Festival(Base):
    __tablename__ = "ric_festivals"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image_base64 = Column(String, nullable=False)
    country_id = Column(Integer, ForeignKey("ric_countries.id"), nullable=False)

    country = relationship("Country", back_populates="festivals")
    awards = relationship("FestivalAward", back_populates="festival")
