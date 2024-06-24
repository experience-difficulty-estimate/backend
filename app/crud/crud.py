from sqlalchemy.orm import Session
from sqlalchemy import func
import app.models.models as models
import app.schemas.schemas as schemas
from database import get_db
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy import stats
from typing import List


def create_experience(
    text: str,
    embedding: List[float],
    difficulty_score: float,
    difficulty_scores: List[float],
    db: Session,
):
    db_experience = models.Experience(
        text=text,
        embedding=embedding,
        difficulty_score=difficulty_score,
        difficulty_scores=difficulty_scores,
    )
    db.add(db_experience)
    db.commit()
    db.refresh(db_experience)
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


def calculate_percentiles(db: Session):
    experiences = db.query(models.Experience).all()

    if not experiences:
        return

    all_scores = [
        exp.difficulty_score for exp in experiences if exp.difficulty_score is not None
    ]

    if not all_scores:
        return

    for experience in experiences:
        if experience.difficulty_score is None:
            continue

        percentile = np.percentile(
            all_scores,
            np.searchsorted(np.sort(all_scores), experience.difficulty_score)
            / len(all_scores)
            * 100,
        )

        db.query(models.Experience).filter(
            models.Experience.id == experience.id
        ).update({"percentile": percentile})

    db.commit()
    logger.info("Percentiles calculated and updated successfully.")


def calculate_percentile(scores, new_score):
    all_scores = np.append(scores, new_score)
    percentile = stats.percentileofscore(all_scores, new_score)
    return percentile


def get_adjacent_experiences(
    difficulty_score: float, db: Session = next(get_db())
) -> tuple[models.Experience | None, models.Experience | None]:
    lower = (
        db.query(models.Experience)
        .filter(models.Experience.difficulty_score < difficulty_score)
        .order_by(models.Experience.difficulty_score.desc())
        .first()
    )
    higher = (
        db.query(models.Experience)
        .filter(models.Experience.difficulty_score > difficulty_score)
        .order_by(models.Experience.difficulty_score)
        .first()
    )
    return lower, higher


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


def update_experience_score(
    experience_id: int, new_score: float, db: Session = next(get_db())
) -> models.Experience:
    experience = (
        db.query(models.Experience)
        .filter(models.Experience.id == experience_id)
        .first()
    )
    if experience:
        experience.difficulty_score = new_score
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
