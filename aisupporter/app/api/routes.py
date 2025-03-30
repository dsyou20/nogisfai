"""
애플리케이션 라우트 설정
"""
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 엔드포인트 모듈 직접 임포트 - 경로 변경 (endpoints 디렉토리 제거)
try:
    from app.api.sensor_data import router as sensor_router
    from app.api.crop_analysis import router as crop_router
    from app.api.ai_control import router as control_router
    from app.api.chatbot import router as chatbot_router
    from app.api.esg_analysis import router as esg_router
    from app.api.openai_api import router as openai_router
    from app.api.record_knowledge import router as record_router
    from app.api.experience_knowledge import router as experience_knowledge_router

    logger.error(f" ****************** 임포트 성공 ****************** ")
    
except ImportError as e:
    logger.error(f" ****************** 임포트 오류: {e} ****************** ")
    # 개발 중에는 모든 모듈이 없을 수 있으므로 가능한 모듈만 임포트
    sensor_router = crop_router = control_router = chatbot_router = esg_router = openai_router = record_router = experience_knowledge_router = None

# 템플릿 설정
templates = Jinja2Templates(directory="app/templates")

def setup_routes(app: FastAPI) -> None:
    """
    FastAPI 애플리케이션에 라우트를 설정합니다.
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
    """
    # 루트 라우트
    @app.get("/")
    async def root(request: Request):
        return templates.TemplateResponse(
            "intro.html",  # 인트로 페이지로 변경
            {"request": request}
        )
    
    # 상태 확인 라우트
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    # 다양한 API 라우터들 등록 - None이 아닌 경우에만 등록
    if sensor_router:
        app.include_router(
            sensor_router,
            prefix="/api/sensors",
            tags=["sensors"],
            responses={404: {"description": "Not found"}},
        )
    

    
    if control_router:
        app.include_router(
            control_router,
            prefix="/api/ai-control",
            tags=["ai-control"],
            responses={404: {"description": "Not found"}},
        )
    
    if chatbot_router:
        app.include_router(
            chatbot_router,
            prefix="/api/chatbot",
            tags=["chatbot"],
            responses={404: {"description": "Not found"}},
        )
    
    if esg_router:
        app.include_router(
            esg_router,
            prefix="/api/esg",
            tags=["esg"],
            responses={404: {"description": "Not found"}},
        )
    
    if record_router:
        app.include_router(
            record_router,
            prefix="/api/data",
            tags=["data"],
            responses={404: {"description": "Not found"}},
        )
    
    if openai_router:
        app.include_router(
            openai_router,
            prefix="/api/openai",
            tags=["openai"],
            responses={404: {"description": "Not found"}},
        )
    
    if crop_router:
        app.include_router(
            crop_router,
            prefix="/api/crops",
            tags=["crops"],
            responses={404: {"description": "Not found"}},
        )
    
    # 경험지식 API 라우터 추가
    if experience_knowledge_router:
        app.include_router(
            experience_knowledge_router,
            prefix="/api/knowledge",
            tags=["knowledge"],
            responses={404: {"description": "Not found"}},
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

    # 재배달력 페이지
    @app.get("/cultivation-calendar")
    async def cultivation_calendar(request: Request):
        return templates.TemplateResponse(
            "cultivation_calendar.html",  # 별도 템플릿 사용
            {"request": request, "title": "재배달력 - 노지AI재배관리시스템", "active_page": "cultivation-calendar"}
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
    
    # 경험지식 관리 페이지 추가
    @app.get("/knowledge-management")
    async def knowledge_management(request: Request):
        return templates.TemplateResponse(
            "knowledge_management.html",  # 템플릿 사용
            {"request": request, "title": "경험지식 관리 - 노지AI재배관리시스템", "active_page": "knowledge-management"}
        )
    
    # AI 진단 페이지
    @app.get("/ai-diagnosis")
    async def ai_diagnosis(request: Request):
        return templates.TemplateResponse(
            "ai_diagnosis.html",  # 템플릿 사용
            {"request": request, "title": "AI 진단 - 노지AI재배관리시스템", "active_page": "ai-diagnosis"}
        )
    
    # AI 처방 페이지
    @app.get("/ai-prescription")
    async def ai_prescription(request: Request):
        return templates.TemplateResponse(
            "ai_prescription.html",  # 템플릿 사용
            {"request": request, "title": "AI 처방 - 노지AI재배관리시스템", "active_page": "ai-prescription"}
        )
    
    # AI 지식 페이지
    @app.get("/ai-knowledge")
    async def ai_knowledge(request: Request):
        return templates.TemplateResponse(
            "ai_knowledge.html",  # 템플릿 사용
            {"request": request, "title": "AI 지식 - 노지AI재배관리시스템", "active_page": "ai-knowledge"}
        )
    
    # AI 파인튜닝 페이지
    @app.get("/ai-finetuning")
    async def ai_finetuning(request: Request):
        return templates.TemplateResponse(
            "ai_finetuning.html",  # 템플릿 사용
            {"request": request, "title": "파인튜닝 - 노지AI재배관리시스템", "active_page": "ai-finetuning"}
        ) 