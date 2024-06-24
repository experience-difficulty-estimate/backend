from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# 환경 변수에서 환경 설정을 가져옵니다. 기본값은 'local'입니다.
app_env = os.getenv("APP_ENV", "local")

# 해당 환경의 .env 파일을 로드합니다.
load_dotenv(f".env.{app_env}")


class Settings(BaseSettings):
    database_url: str
    app_env: str = app_env
    debug: bool
    openai_api_key: str

    class Config:
        env_file = f".env.{app_env}"
        env_file_encoding = "utf-8"


settings = Settings()

if (
    settings.app_env == "production"
    and "your_production_db_identifier" not in settings.database_url
):
    raise ValueError(
        "Production environment detected but production database URL not found!"
    )
