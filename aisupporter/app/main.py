"""
노지AI재배관리시스템 애플리케이션 설정
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.api.routes import setup_routes

# scripts의 init_db 모듈에서 초기화 함수 가져오기
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
from scripts.init_db import init_db

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(testing=False):
    """애플리케이션 팩토리"""
    # FastAPI 앱 생성
    app = FastAPI(
        title="노지AI재배관리시스템",
        description="AI·센서·영상·챗봇·ESG 분석을 통합한 재배관리 지원시스템",
        version="0.1.0"
    )
    
    # 데이터베이스 초기화 (없으면 생성)
    logger.info("애플리케이션 시작 시 데이터베이스 초기화 실행")
    try:
        init_db()
        logger.info("데이터베이스 초기화 완료")
    except Exception as e:
        logger.error(f"데이터베이스 초기화 중 오류 발생: {e}")
    
    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if testing else settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 정적 파일 및 템플릿 설정
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # 라우터 설정
    setup_routes(app)
    
    return app 