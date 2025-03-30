"""
애플리케이션 라우트 설정
"""
from fastapi import Request
from fastapi.templating import Jinja2Templates

# 엔드포인트 모듈 직접 임포트 - 경로 변경 (endpoints 디렉토리 제거)
try:
    from app.api.sensor_data import router as sensor_router
    from app.api.crop_analysis import router as crop_router
    from app.api.ai_control import router as control_router
    from app.api.chatbot import router as chatbot_router
    from app.api.esg_analysis import router as esg_router
    from app.api.openai_api import router as openai_router
    from app.api.record_knowledge import router as record_router
except ImportError as e:
    print(f"임포트 오류: {e}")
    # 개발 중에는 모든 모듈이 없을 수 있으므로 가능한 모듈만 임포트
    sensor_router = crop_router = control_router = chatbot_router = esg_router = openai_router = record_router = None

# 템플릿 설정
templates = Jinja2Templates(directory="app/templates")

def setup_routes(app):
    """
    모든 애플리케이션 라우트 설정
    이 함수는 main.py의 create_app() 내에서 호출됨
    """
    # API 라우터 등록 (존재하는 라우터만)
    if sensor_router:
        app.include_router(sensor_router, prefix="/api/sensors", tags=["센서 데이터"])
    if crop_router:
        app.include_router(crop_router, prefix="/api/crops", tags=["작물 분석"])
    if control_router:
        app.include_router(control_router, prefix="/api/control", tags=["AI 제어"])
    if chatbot_router:
        app.include_router(chatbot_router, prefix="/api/chatbot", tags=["AI 챗봇"])
    if esg_router:
        app.include_router(esg_router, prefix="/api/esg", tags=["ESG 분석"])
    if openai_router:
        app.include_router(openai_router, prefix="/api/openai", tags=["OpenAI API"])
    if record_router:
        app.include_router(record_router, prefix="/api/data", tags=["기록지식 데이터"])
    
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

    # 파인튜닝 페이지
    @app.get("/ai-finetuning")
    async def ai_finetuning(request: Request):
        return templates.TemplateResponse(
            "ai_finetuning.html",
            {"request": request, "title": "파인튜닝 - 노지AI재배관리시스템", "active_page": "ai-finetuning"}
        )

    # 설정 페이지
    @app.get("/settings")
    async def settings_page(request: Request):
        return templates.TemplateResponse(
            "settings.html",  # 별도 템플릿 사용
            {"request": request, "title": "설정 - 노지AI재배관리시스템", "active_page": "settings"}
        )

    # 팜맵 예제 페이지
    @app.get("/farm-map-example")
    async def farm_map_example_page(request: Request):
        return templates.TemplateResponse(
            "example-farm-map.html",
            {"request": request, "title": "팜맵 예제", "active_page": "farm-map-example"}
        ) 