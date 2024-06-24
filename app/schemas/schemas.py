from pydantic import BaseModel
from typing import Optional, List


class ExperienceBase(BaseModel):
    text: str


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceWithScore(ExperienceBase):
    id: int
    difficulty_score: float
    relative_difficulty: float


class AdjacentExperiences(BaseModel):
    lower: Optional[ExperienceWithScore] = None
    higher: Optional[ExperienceWithScore] = None


class ExperienceResponse(BaseModel):
    user_experience: ExperienceWithScore
    adjacent_experiences: AdjacentExperiences
    total_experiences: int


class UserComparisonInput(BaseModel):
    experience_id: int
    is_more_difficult_than_lower: bool
    is_less_difficult_than_higher: bool


class FinalExperienceResponse(ExperienceWithScore):
    pass


class Config:
    from_attributes = True
