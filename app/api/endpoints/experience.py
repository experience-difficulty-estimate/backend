import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas import schemas
from app.crud import crud
from app.utils.gpt import analyze_experience, get_embedding
from app.database import get_db
from sklearn.metrics.pairwise import cosine_similarity

router = APIRouter()
logger = logging.getLogger(__name__)


def find_similar_experience(
    new_embedding: list[float], db: Session, similarity_threshold: float = 0.95
):
    experiences = db.query(crud.models.Experience).all()
    for exp in experiences:
        similarity = cosine_similarity([new_embedding], [exp.embedding])[0][0]
        if similarity > similarity_threshold:
            return exp
    return None


@router.post("/estimate", response_model=schemas.ExperienceResponse)
async def estimate_difficulty(
    experience: schemas.ExperienceCreate, db: Session = Depends(get_db)
) -> schemas.ExperienceResponse:
    try:
        embedding = get_embedding(experience.text)
        similar_exp = find_similar_experience(embedding, db)

        if similar_exp:
            difficulty_score = similar_exp.difficulty_score
            logger.info(
                f"Found similar experience: {similar_exp.text}. Using its difficulty score: {difficulty_score}"
            )
        else:
            analysis = analyze_experience(experience.text)
            difficulty_score = analysis["single_score"]
            logger.info(
                f"No similar experience found. Using GPT analysis. Difficulty score: {difficulty_score}"
            )

        new_experience = crud.create_experience(
            text=experience.text,
            embedding=embedding,
            difficulty_score=difficulty_score,
            db=db,
        )

        crud.calculate_percentiles(db)
        lower_exp, higher_exp = crud.get_adjacent_experiences(
            new_experience.difficulty_score, db
        )
        total_count = crud.get_total_experiences_count(db)

        return schemas.ExperienceResponse(
            user_experience=schemas.ExperienceWithScore(
                id=new_experience.id,
                text=new_experience.text,
                difficulty_score=new_experience.difficulty_score,
                percentile=new_experience.percentile,
            ),
            adjacent_experiences=schemas.AdjacentExperiences(
                lower=(
                    schemas.ExperienceWithScore(
                        id=lower_exp.id,
                        text=lower_exp.text,
                        difficulty_score=lower_exp.difficulty_score,
                        percentile=lower_exp.percentile,
                    )
                    if lower_exp
                    else None
                ),
                higher=(
                    schemas.ExperienceWithScore(
                        id=higher_exp.id,
                        text=higher_exp.text,
                        difficulty_score=higher_exp.difficulty_score,
                        percentile=higher_exp.percentile,
                    )
                    if higher_exp
                    else None
                ),
            ),
            total_experiences=total_count,
        )
    except Exception as e:
        logger.error(f"Error in estimate_difficulty: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare", response_model=schemas.FinalExperienceResponse)
async def compare_experiences(
    comparison: schemas.UserComparisonInput, db: Session = Depends(get_db)
) -> schemas.FinalExperienceResponse:
    try:
        logger.info(
            f"Received comparison for experience ID: {comparison.experience_id}"
        )

        experience = crud.get_experience_by_id(comparison.experience_id, db)
        if not experience:
            logger.error(f"Experience not found: {comparison.experience_id}")
            raise HTTPException(status_code=404, detail="Experience not found")

        crud.create_comparison(
            experience_id=comparison.experience_id,
            is_more_difficult_than_lower=comparison.is_more_difficult_than_lower,
            is_less_difficult_than_higher=comparison.is_less_difficult_than_higher,
            db=db,
        )

        # 사용자 비교 결과에 따라 난이도 점수 조정
        if (
            comparison.is_more_difficult_than_lower
            and comparison.is_less_difficult_than_higher
        ):
            # 현재 난이도 유지
            pass
        elif comparison.is_more_difficult_than_lower:
            # 난이도 약간 증가
            experience.difficulty_score *= 1.05
        elif comparison.is_less_difficult_than_higher:
            # 난이도 약간 감소
            experience.difficulty_score *= 0.95
        else:
            # 사용자가 양쪽 모두 거부한 경우, 더 큰 조정 필요
            if experience.difficulty_score > 50:
                experience.difficulty_score *= 0.9
            else:
                experience.difficulty_score *= 1.1

        experience.difficulty_score = max(0, min(100, experience.difficulty_score))
        logger.info(f"Adjusted difficulty score: {experience.difficulty_score}")

        # 난이도 점수 업데이트 및 퍼센타일 재계산
        updated_experience = crud.update_experience_score(
            experience_id=experience.id, new_score=experience.difficulty_score, db=db
        )
        crud.calculate_percentiles(db)

        return schemas.FinalExperienceResponse(
            id=updated_experience.id,
            text=updated_experience.text,
            difficulty_score=updated_experience.difficulty_score,
            percentile=updated_experience.percentile,
            final_percentile=updated_experience.percentile,
        )
    except Exception as e:
        logger.error(f"Error in compare_experiences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
