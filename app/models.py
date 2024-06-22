from sqlalchemy import Column, Integer, String, ARRAY, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Experience(Base):
    __tablename__ = "experiences"

    id: int = Column(Integer, primary_key=True, index=True)
    text: str = Column(String, index=True)
    embedding: list[float] = Column(ARRAY(Float))
    difficulty_scores: list[float] = Column(ARRAY(Float))
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
