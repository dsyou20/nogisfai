"""
데이터베이스 세션 관리
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 데이터베이스 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.SQL_ECHO
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 의존성 주입을 위한 함수
def get_db():
    """
    FastAPI 라우터 의존성으로 사용할 데이터베이스 세션을 제공하는 함수
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 