from sqlalchemy import (
    Column,
    Integer,
    String,
    ARRAY,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String, unique=True, index=True)
    age: int = Column(Integer)
    occupation: str = Column(String)
    hobbies: list[str] = Column(ARRAY(String))
    past_experiences: JSON = Column(JSON)  # 과거 경험을 JSON 형태로 저장
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    experiences = relationship("Experience", back_populates="user")


class Experience(Base):
    __tablename__ = "experiences"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey("users.id"))
    text: str = Column(String, index=True)
    category: str = Column(String, index=True)  # 경험 카테고리 추가
    tags: list[str] = Column(ARRAY(String))  # 경험 태그 추가
    embedding: list[float] = Column(ARRAY(Float))
    difficulty_score: float = Column(Float)  # 절대적 난이도 점수
    relative_difficulty: float = Column(Float)  # 상대적 난이도 (퍼센타일)
    difficulty_scores: list[float] = Column(ARRAY(Float))  # 기존 difficulty_scores 유지
    user_feedback_score: float = Column(Float)  # 사용자 피드백 점수 추가
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="experiences")
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
    compared_experience_id: int = Column(
        Integer,
        ForeignKey(
            "experiences.id",
            ondelete="CASCADE",
            name="fk_comparison_compared_experience_id",
        ),
    )
    is_more_difficult: bool = Column(Boolean)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    experience = relationship(
        "Experience", foreign_keys=[experience_id], back_populates="comparisons"
    )
    compared_experience = relationship(
        "Experience", foreign_keys=[compared_experience_id]
    )


class ValidationFeedback(Base):
    __tablename__ = "validation_feedbacks"

    id: int = Column(Integer, primary_key=True, index=True)
    experience_id: int = Column(Integer, ForeignKey("experiences.id"))
    user_id: int = Column(Integer, ForeignKey("users.id"))
    feedback_score: float = Column(Float)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    experience = relationship("Experience")
    user = relationship("User")
