from sqlalchemy.orm import Session
from sqlalchemy import func
import app.models.models as models
import app.schemas.schemas as schemas
from database import get_db
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy import stats
from typing import List


def calculate_relative_difficulty(db: Session, difficulty_score: float) -> float:
    total_experiences = db.query(func.count(models.Experience.id)).scalar()
    lower_experiences = (
        db.query(func.count(models.Experience.id))
        .filter(models.Experience.difficulty_score <= difficulty_score)
        .scalar()
    )
    return (
        (lower_experiences / total_experiences) * 100 if total_experiences > 0 else 50.0
    )


def update_all_relative_difficulties(db: Session):
    experiences = (
        db.query(models.Experience).order_by(models.Experience.difficulty_score).all()
    )
    total = len(experiences)
    for i, exp in enumerate(experiences):
        exp.relative_difficulty = ((i + 1) / total) * 100
    db.commit()


def create_experience(
    text: str,
    embedding: list[float],
    difficulty_score: float,
    difficulty_scores: list[float],
    db: Session,
) -> models.Experience:
    relative_difficulty = calculate_relative_difficulty(db, difficulty_score)
    db_experience = models.Experience(
        text=text,
        embedding=embedding,
        difficulty_score=difficulty_score,
        relative_difficulty=relative_difficulty,
        difficulty_scores=difficulty_scores,
    )
    db.add(db_experience)
    db.commit()
    db.refresh(db_experience)

    # 모든 경험의 상대적 난이도 업데이트
    update_all_relative_difficulties(db)

    return db_experience


def get_similar_experience(
    embedding: list[float], threshold: float = 0.9, db: Session = next(get_db())
) -> tuple[models.Experience | None, float]:
    experiences = db.query(models.Experience).all()
    if not experiences:
        return None, 0

    similarities = [
        (exp, cosine_similarity([embedding], [exp.embedding])[0][0])
        for exp in experiences
    ]

    most_similar = max(similarities, key=lambda x: x[1])
    if most_similar[1] > threshold:
        return most_similar
    return None, 0


import logging
from sqlalchemy.orm import Session
from app.models.models import Experience
import numpy as np

logger = logging.getLogger(__name__)


def recalculate_difficulties(db: Session):
    experiences = (
        db.query(models.Experience)
        .order_by(models.Experience.relative_difficulty)
        .all()
    )
    total = len(experiences)
    for i, exp in enumerate(experiences):
        exp.relative_difficulty = ((i + 1) / total) * 100
        exp.difficulty_score = exp.relative_difficulty  # 또는 다른 적절한 변환 로직
    db.commit()


def get_adjacent_experiences(
    difficulty_score: float, db: Session = next(get_db())
) -> tuple[models.Experience | None, models.Experience | None]:
    logger.info(
        f"Getting adjacent experiences for difficulty score: {difficulty_score}"
    )
    try:
        lower = (
            db.query(models.Experience)
            .filter(models.Experience.difficulty_score.isnot(None))
            .filter(models.Experience.difficulty_score < difficulty_score)
            .order_by(models.Experience.difficulty_score.desc())
            .first()
        )
        higher = (
            db.query(models.Experience)
            .filter(models.Experience.difficulty_score.isnot(None))
            .filter(models.Experience.difficulty_score > difficulty_score)
            .order_by(models.Experience.difficulty_score)
            .first()
        )
        logger.info(
            f"Adjacent experiences found. Lower: {'Found' if lower else 'None'}, Higher: {'Found' if higher else 'None'}"
        )
        return lower, higher
    except Exception as e:
        logger.error(f"Error in get_adjacent_experiences: {str(e)}", exc_info=True)
        raise


def create_comparison(
    experience_id: int,
    is_more_difficult_than_lower: bool,
    is_less_difficult_than_higher: bool,
    db: Session,
) -> models.Comparison:
    db_comparison = models.Comparison(
        experience_id=experience_id,
        is_more_difficult_than_lower=is_more_difficult_than_lower,
        is_less_difficult_than_higher=is_less_difficult_than_higher,
    )
    db.add(db_comparison)
    db.commit()
    db.refresh(db_comparison)
    return db_comparison


def update_experience_relative_difficulty(
    experience_id: int, new_relative_difficulty: float, db: Session
) -> models.Experience:
    experience = (
        db.query(models.Experience)
        .filter(models.Experience.id == experience_id)
        .first()
    )
    if experience:
        experience.relative_difficulty = new_relative_difficulty
        db.commit()
        db.refresh(experience)
    return experience


def get_experience_by_id(
    experience_id: int, db: Session = next(get_db())
) -> models.Experience:
    return (
        db.query(models.Experience)
        .filter(models.Experience.id == experience_id)
        .first()
    )


def get_total_experiences_count(db: Session = next(get_db())) -> int:
    return db.query(func.count(models.Experience.id)).scalar()
