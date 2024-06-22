from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def create_experience(
    text: str,
    embedding: list[float],
    difficulty_scores: list[float],
    db: Session = next(get_db()),
) -> models.Experience:
    db_experience = models.Experience(
        text=text, embedding=embedding, difficulty_scores=difficulty_scores
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
