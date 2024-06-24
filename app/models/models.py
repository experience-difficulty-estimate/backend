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
    difficulty_score: float = Column(Float)  # 절대적 난이도 점수
    relative_difficulty: float = Column(Float)  # 상대적 난이도 (퍼센타일)
    difficulty_scores: list[float] = Column(ARRAY(Float))  # 기존 difficulty_scores 유지
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    comparisons = relationship(
        "Comparison", back_populates="experience", cascade="all, delete-orphan"
    )


class Comparison(Base):
    __tablename__ = "comparisons"

    id: int = Column(Integer, primary_key=True, index=True)
    experience_id: int = Column(
        Integer,
        ForeignKey(
            "experiences.id", ondelete="CASCADE", name="fk_comparison_experience_id"
        ),
    )
    is_more_difficult_than_lower: bool = Column(Boolean)
    is_less_difficult_than_higher: bool = Column(Boolean)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    experience = relationship("Experience", back_populates="comparisons")
