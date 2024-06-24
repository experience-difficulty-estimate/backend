from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from app import models
from loguru import logger


def clean_null_difficulty_scores(db: Session = next(get_db())):
    null_records = (
        db.query(models.Experience)
        .filter(models.Experience.difficulty_score.is_(None))
        .all()
    )

    for record in null_records:
        # 여기서 레코드를 업데이트하거나 삭제합니다.
        # 예: 레코드 삭제
        db.delete(record)
        # 또는 예: 기본값으로 업데이트
        # record.difficulty_score = 0

    db.commit()
    logger.info(f"Cleaned {len(null_records)} records with null difficulty scores")
