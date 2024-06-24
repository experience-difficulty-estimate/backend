from sqlalchemy import (
    Column,
    Integer,
    String,
    ARRAY,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Experience(Base):
    __tablename__ = "experiences"

    id: int = Column(Integer, primary_key=True, index=True)
    text: str = Column(String, index=True)
    embedding: list[float] = Column(ARRAY(Float))
    difficulty_score: float = Column(Float)  # 새로운 단일 난이도 점수
    difficulty_scores: list[float] = Column(ARRAY(Float))  # 기존 difficulty_scores 유지
    percentile: float = Column(Float, nullable=True)  # 퍼센타일 정보
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    feedbacks = relationship("Feedback", back_populates="experience")
    comparisons = relationship("Comparison", back_populates="experience")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: int = Column(Integer, primary_key=True, index=True)
    experience_id: int = Column(
        Integer, ForeignKey("experiences.id", name="fk_feedback_experience_id")
    )
    agreement_score: float = Column(Float)  # 1-5 scale, where 5 is strong agreement
    comment: str = Column(String, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    experience = relationship("Experience", back_populates="feedbacks")


class Comparison(Base):
    __tablename__ = "comparisons"

    id: int = Column(Integer, primary_key=True, index=True)
    experience_id: int = Column(
        Integer, ForeignKey("experiences.id", name="fk_comparison_experience_id")
    )
    is_more_difficult_than_lower: bool = Column(Boolean)
    is_less_difficult_than_higher: bool = Column(Boolean)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    experience = relationship("Experience", back_populates="comparisons")
