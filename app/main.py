from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.database import engine
import app.models.models as models
from app.config import settings
import logging
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Experience Difficulty Estimator", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "https://difficulty-estimation-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 포함
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application...")
    # 데이터베이스 테이블 생성
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application...")


@app.get("/")
def get_root():
    return {
        "message": "Welcome to Experience Difficulty Estimator API",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=settings.DEBUG)
