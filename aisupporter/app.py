"""
스마트 콩 재배 AI 자동제어 시스템 메인 애플리케이션
"""
import argparse
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api import sensor_data, crop_analysis, ai_control, chatbot, esg_analysis
from app.core.config import settings

# 명령행 인자 파싱
parser = argparse.ArgumentParser(description="스마트 콩 재배 AI 자동제어 시스템")
parser.add_argument("--prod", action="store_true", help="프로덕션 모드로 실행")
args = parser.parse_args()

# FastAPI 앱 생성
app = FastAPI(
    title="스마트 콩 재배 AI 자동제어 시스템",
    description="AI·센서·영상·챗봇·ESG 분석을 통합한 자동 제어 시스템",
    version="0.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not args.prod else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# API 라우터 등록
app.include_router(sensor_data.router, prefix="/api/sensors", tags=["센서 데이터"])
app.include_router(crop_analysis.router, prefix="/api/crops", tags=["작물 분석"])
app.include_router(ai_control.router, prefix="/api/control", tags=["AI 제어"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["AI 챗봇"])
app.include_router(esg_analysis.router, prefix="/api/esg", tags=["ESG 분석"])

# 메인 페이지
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "스마트 콩 재배 AI 자동제어 시스템"}
    )

# 대시보드 페이지
@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "대시보드 - 스마트 콩 재배 AI 자동제어 시스템"}
    )

# 환경 변수에 따른 설정
if __name__ == "__main__":
    # 프로덕션 모드 여부에 따른 설정
    host = settings.HOST
    port = settings.PORT
    reload = not args.prod
    
    # 시작 메시지
    mode = "프로덕션" if args.prod else "개발"
    print(f"스마트 콩 재배 AI 자동제어 시스템을 {mode} 모드로 실행합니다.")
    print(f"서버 주소: http://{host}:{port}")
    
    # 서버 실행
    if reload:
        # reload 옵션을 사용할 때는 문자열 경로로 전달
        uvicorn.run("app:app", host=host, port=port, reload=reload)
    else:
        # reload 옵션을 사용하지 않을 때는 객체로 전달
        uvicorn.run(app, host=host, port=port) 