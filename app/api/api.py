from fastapi import APIRouter
from app.api.endpoints import experience

api_router = APIRouter()
api_router.include_router(experience.router, prefix="/api", tags=["experience"])
