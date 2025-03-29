"""
노지AI재배관리시스템 메인 애플리케이션
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
parser = argparse.ArgumentParser(description="노지AI재배관리시스템")
parser.add_argument("--prod", action="store_true", help="프로덕션 모드로 실행")
args = parser.parse_args()

# FastAPI 앱 생성
app = FastAPI(
    title="노지AI재배관리시스템",
    description="AI·센서·영상·챗봇·ESG 분석을 통합한 재배관리 지원시스템",
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
        "intro.html",  # 인트로 페이지로 변경
        {"request": request}
    )

# 대시보드 페이지
@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "대시보드 - 노지AI재배관리시스템", "active_page": "dashboard"}
    )

# 전체현황 페이지
@app.get("/overview")
async def overview(request: Request):
    return templates.TemplateResponse(
        "overview.html",  # 별도 템플릿 사용
        {"request": request, "title": "전체현황 - 노지AI재배관리시스템", "active_page": "overview"}
    )

# 자동 제어 페이지
@app.get("/control")
async def control(request: Request):
    return templates.TemplateResponse(
        "control.html",  # 별도 템플릿 사용
        {"request": request, "title": "자동 제어 - 노지AI재배관리시스템", "active_page": "control"}
    )

# 영상 분석 페이지
@app.get("/video")
async def video(request: Request):
    return templates.TemplateResponse(
        "video.html",  # 별도 템플릿 사용
        {"request": request, "title": "영상분석 - 노지AI재배관리시스템", "active_page": "video"}
    )

# 수분분석 페이지
@app.get("/moisture-nutrition")
async def moisture_nutrition(request: Request):
    return templates.TemplateResponse(
        "moisture_nutrition.html",  # 별도 템플릿 사용
        {"request": request, "title": "수분분석 - 노지AI재배관리시스템", "active_page": "moisture-nutrition"}
    )

# 영양분석 페이지
@app.get("/impact")
async def impact(request: Request):
    return templates.TemplateResponse(
        "impact.html",  # 별도 템플릿 사용
        {"request": request, "title": "영양분석 - 노지AI재배관리시스템", "active_page": "impact"}
    )

# 수확예측 페이지
@app.get("/yield")
async def yield_prediction(request: Request):
    return templates.TemplateResponse(
        "yield.html",  # 별도 템플릿 사용
        {"request": request, "title": "수확예측 - 노지AI재배관리시스템", "active_page": "yield"}
    )

# ESG 분석 페이지
@app.get("/esg")
async def esg(request: Request):
    return templates.TemplateResponse(
        "esg.html",  # 별도 템플릿 사용
        {"request": request, "title": "ESG 분석 - 노지AI재배관리시스템", "active_page": "esg"}
    )

# AI 챗봇 페이지
@app.get("/chatbot")
async def chatbot_page(request: Request):
    return templates.TemplateResponse(
        "chatbot.html",  # 별도 템플릿 사용
        {"request": request, "title": "AI 챗봇 - 노지AI재배관리시스템", "active_page": "chatbot"}
    )

# 솔루션 소개 페이지
@app.get("/intro")
async def intro_page(request: Request):
    return templates.TemplateResponse(
        "intro.html",
        {"request": request, "title": "솔루션 소개 - 노지AI재배관리시스템", "active_page": "intro"}
    )

# AI 진단 페이지
@app.get("/ai-diagnosis")
async def ai_diagnosis(request: Request):
    return templates.TemplateResponse(
        "ai_diagnosis.html",
        {"request": request, "title": "AI 진단 - 노지AI재배관리시스템", "active_page": "ai-diagnosis"}
    )

# AI 처방 페이지
@app.get("/ai-prescription")
async def ai_prescription(request: Request):
    return templates.TemplateResponse(
        "ai_prescription.html",
        {"request": request, "title": "AI 처방 - 노지AI재배관리시스템", "active_page": "ai-prescription"}
    )

# AI 지식 페이지
@app.get("/ai-knowledge")
async def ai_knowledge(request: Request):
    return templates.TemplateResponse(
        "ai_knowledge.html",
        {"request": request, "title": "AI 지식 - 노지AI재배관리시스템", "active_page": "ai-knowledge"}
    )

# 설정 페이지
@app.get("/settings")
async def settings_page(request: Request):
    return templates.TemplateResponse(
        "settings.html",  # 별도 템플릿 사용
        {"request": request, "title": "설정 - 노지AI재배관리시스템", "active_page": "settings"}
    )

# 환경 변수에 따른 설정
if __name__ == "__main__":
    # 프로덕션 모드 여부에 따른 설정
    host = settings.HOST
    port = settings.PORT
    reload = not args.prod
    
    # 항상 테스트 모드로 설정
    reload = True
    
    # 시작 메시지
    mode = "테스트" if reload else "프로덕션"
    print(f"노지AI재배관리시스템을 {mode} 모드로 실행합니다.")
    print(f"서버 주소: http://{host}:{port}")
    
    # 서버 실행 - main.py에서는 main:app으로 실행
    uvicorn.run("main:app", host=host, port=port, reload=reload) 