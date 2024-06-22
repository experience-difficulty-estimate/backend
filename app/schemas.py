from pydantic import BaseModel


class ExperienceBase(BaseModel):
    text: str


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceResponse(ExperienceBase):
    id: int
    difficulty_scores: list[float]
    total_difficulty: float
    level: int
    similarity: float

    class Config:
        from_attributes = True
