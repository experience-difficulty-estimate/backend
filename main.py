from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app import models, crud, schemas
from app.utils import get_embedding, get_difficulty_scores

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React 앱의 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


@app.post("/api/estimate", response_model=schemas.ExperienceResponse)
async def estimate_difficulty(
    experience: schemas.ExperienceCreate,
) -> schemas.ExperienceResponse:
    embedding = get_embedding(experience.text)
    similar_exp, similarity = crud.get_similar_experience(embedding)

    if similar_exp and similarity > 0.95:
        difficulty_scores = similar_exp.difficulty_scores
    else:
        difficulty_scores = get_difficulty_scores(experience.text)

    total_difficulty = sum(difficulty_scores) / len(difficulty_scores)
    level = int(total_difficulty / 10) + 1

    new_experience = crud.create_experience(
        experience.text, embedding, difficulty_scores
    )

    return schemas.ExperienceResponse(
        id=new_experience.id,
        text=new_experience.text,
        difficulty_scores=new_experience.difficulty_scores,
        total_difficulty=total_difficulty,
        level=level,
        similarity=similarity if similar_exp else 0,
    )