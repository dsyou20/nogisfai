"""
애플리케이션 설정 관리 모듈
"""
import os
from pydantic import BaseModel
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings(BaseModel):
    """
    애플리케이션 설정 관리 클래스
    """
    # 기본 설정
    APP_NAME: str = "노지AI재배관리시스템"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    
    # 보안 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-for-development")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # 데이터베이스 설정
    DB_PATH: str = os.getenv("DB_PATH", "/home/jovyan/data/soybean_farm.duckdb")
    PARQUET_DIR: str = os.getenv("PARQUET_DIR", "/home/jovyan/data/parquet")
    
    # SQLAlchemy 데이터베이스 설정
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "false").lower() == "true"
    
    # LLM 설정
    LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-4o")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    
    # 센서 및 제어 설정
    SENSOR_UPDATE_INTERVAL: int = int(os.getenv("SENSOR_UPDATE_INTERVAL", "300"))  # 5분
    CONTROL_CHECK_INTERVAL: int = int(os.getenv("CONTROL_CHECK_INTERVAL", "3600"))  # 1시간
    
    # ESG 분석 설정
    ESG_REPORT_INTERVAL: str = os.getenv("ESG_REPORT_INTERVAL", "monthly")  # daily, weekly, monthly

# 설정 인스턴스 생성
settings = Settings()

# 환경에 따른 설정 재정의
if settings.DEBUG:
    # 개발 환경 전용 설정
    print("개발 환경으로 실행 중입니다.")
else:
    # 프로덕션 환경 전용 설정
    print("프로덕션 환경으로 실행 중입니다.") 