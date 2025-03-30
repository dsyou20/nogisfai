"""
API 모듈 초기화
"""
# 순환 임포트를 방지하기 위해 아무 것도 임포트하지 않음
# routes.py에서 필요한 모듈을 직접 임포트함

# 모듈 이름만 노출
__all__ = [
    "routes",
    "sensor_data",
    "crop_analysis",
    "ai_control",
    "chatbot",
    "esg_analysis",
    "openai_api",
    "record_knowledge"
]
