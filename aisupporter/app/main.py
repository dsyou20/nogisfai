"""
노지AI재배관리시스템 애플리케이션 설정
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import setup_routes

def create_app(testing=False):
    """애플리케이션 팩토리"""
    # FastAPI 앱 생성
    app = FastAPI(
        title="노지AI재배관리시스템",
        description="AI·센서·영상·챗봇·ESG 분석을 통합한 재배관리 지원시스템",
        version="0.1.0"
    )
    
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