import sys
import os
import logging
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# 프로젝트 루트 디렉토리 경로
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(project_root)

# 이 부분은 models.py에서 정의한 모델들을 import하는 곳입니다.
from app.models.models import Base

# .env 파일 로드
app_env = os.getenv("APP_ENV", "local")
dotenv_path = os.path.join(project_root, f".env.{app_env}")
load_dotenv(dotenv_path)

# 로거 설정
logger = logging.getLogger("alembic.env")

# 환경 변수가 올바르게 로드되었는지 확인
database_url = os.getenv("DATABASE_URL")
logger.info(f"Loaded environment: {app_env}")
logger.info(f"Loading .env file from: {dotenv_path}")
logger.info(f"DATABASE_URL: {database_url}")

# Alembic Config 객체 가져오기
config = context.config

# 파일 구성 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLAlchemy MetaData 객체 설정
target_metadata = Base.metadata

# 환경 변수에서 데이터베이스 URL 설정
if not database_url:
    raise ValueError("DATABASE_URL environment variable not set")

config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
