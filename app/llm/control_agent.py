"""
LLM 기반 제어 판단 에이전트
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
# 임포트 오류 처리를 위한 try-except 블록 추가
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    # 임포트 실패 시 모의 구현 제공
    class ChatOpenAI:
        def __init__(self, model=None, temperature=0, api_key=None):
            self.model = model
            self.temperature = temperature
            self.api_key = api_key
            
        def invoke(self, messages):
            # 모의 응답 생성
            class MockResponse:
                def __init__(self, content):
                    self.content = content
            return MockResponse("""
            {
                "recommended_actions": [],
                "reasoning": "테스트 환경에서 실행 중입니다. 실제 LLM API가 연결되지 않았습니다.",
                "risk_assessment": {"risk_level": "low", "factors": ["테스트 환경"]},
                "confidence_score": 0.1
            }
            """)

try:
    import langgraph
    from langgraph.graph import StateGraph, END
except ImportError:
    # langgraph 임포트 실패 처리
    class StateGraph:
        def __init__(self, **kwargs):
            pass
            
    END = "END"

from app.core.config import settings
from app.models.control import (
    LLMControlInput, LLMControlOutput, ControlRequest, 
    ControlActionType
)

# 시스템 프롬프트
SYSTEM_PROMPT = """
당신은 스마트 콩 재배 시스템의 AI 제어 전문가입니다.
센서 데이터, 작물 상태, 과거 데이터 추세, 기상 예보 및 이전 제어 작업을 분석하여
최적의 제어 결정을 내려야 합니다.

결정 프로세스:
1. 모든 입력 데이터를 종합적으로 분석하세요.
2. 작물의 생장 단계와 건강 상태를 고려하세요.
3. 다음 제어 유형을 고려하세요: 관수(irrigation), 비료(fertilization), 방제(pest_control), 환경(environmental).
4. 모든 추천 작업에 대한 상세한 근거를 제공하세요.
5. 각 결정의 위험 평가와 신뢰도 점수를 제공하세요.

응답 형식:
- recommended_actions: 추천 제어 동작 목록
- reasoning: 추천 이유에 대한 상세 설명
- risk_assessment: 위험 평가
- confidence_score: 판단 신뢰도 점수 (0-1)

결정 시 고려해야 할 콩 재배의 주요 요구 사항:
- 수분: 생육 단계에 따라 35-45% 유지
- 온도: 20-30°C 범위 유지
- 질소, 인, 칼륨: 생육 단계별 최적 수준 유지
- 병해충: 조기 감지 및 예방적 처리
- 에너지 효율: 불필요한 제어 작업 최소화
"""

# LLM 모델 설정
def get_llm():
    """LLM 모델 인스턴스 반환"""
    api_key = settings.LLM_API_KEY
    model_name = settings.LLM_MODEL
    
    # OpenAI 모델 사용
    if model_name.startswith("openai/"):
        model = model_name.replace("openai/", "")
        return ChatOpenAI(
            model=model,
            temperature=0.1,
            api_key=api_key
        )
    
    # 다른 모델 지원도 추가 가능
    raise ValueError(f"지원되지 않는 LLM 모델: {model_name}")

def format_input_for_llm(input_data: LLMControlInput) -> str:
    """LLM 입력용으로 데이터 포맷팅"""
    return f"""
현재 센서 데이터:
{format_dict(input_data.sensor_data)}

작물 상태:
{format_dict(input_data.crop_status)}

과거 데이터 추세:
{format_dict(input_data.historical_trends)}

날씨 예보:
{format_dict(input_data.weather_forecast) if input_data.weather_forecast else "데이터 없음"}

이전 제어 동작:
{format_list(input_data.previous_actions)}

시스템 제약 조건:
{format_dict(input_data.system_constraints)}
"""

def format_dict(data: Dict[str, Any], indent: int = 0) -> str:
    """사전 데이터를 문자열로 포맷팅"""
    result = []
    spaces = " " * indent
    
    for key, value in data.items():
        if isinstance(value, dict):
            result.append(f"{spaces}- {key}:")
            result.append(format_dict(value, indent + 2))
        elif isinstance(value, list):
            result.append(f"{spaces}- {key}:")
            for item in value:
                if isinstance(item, dict):
                    result.append(format_dict(item, indent + 2))
                else:
                    result.append(f"{spaces}  - {item}")
        else:
            result.append(f"{spaces}- {key}: {value}")
    
    return "\n".join(result)

def format_list(data: List[Any], indent: int = 0) -> str:
    """리스트 데이터를 문자열로 포맷팅"""
    if not data:
        return "  없음"
    
    result = []
    spaces = " " * indent
    
    for i, item in enumerate(data):
        if isinstance(item, dict):
            result.append(f"{spaces}{i+1}. 동작:")
            result.append(format_dict(item, indent + 2))
        else:
            result.append(f"{spaces}{i+1}. {item}")
    
    return "\n".join(result)

def analyze_control_decision(input_data: LLMControlInput) -> LLMControlOutput:
    """
    LLM을 사용하여 제어 결정 분석
    
    Args:
        input_data: 제어 결정을 위한 입력 데이터
        
    Returns:
        LLM 분석 결과
    """
    # LLM 모델 획득
    llm = get_llm()
    
    # 입력 데이터 포맷팅
    formatted_input = format_input_for_llm(input_data)
    
    # 출력 파서 설정
    parser = JsonOutputParser()
    
    # LLM 호출
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"다음 상태를 분석하고 최적의 제어 결정을 내려주세요:\n\n{formatted_input}")
    ]
    
    # 실제 LLM이 없는 경우를 위한 샘플 응답
    # 실제 구현에서는 이 부분이 llm.invoke(messages)로 대체됨
    try:
        # response = llm.invoke(messages)
        # output_dict = parser.parse(response.content)
        
        # 샘플 응답 생성
        output_dict = generate_sample_response(input_data)
    except Exception as e:
        print(f"LLM 호출 중 오류 발생: {str(e)}")
        # 오류 발생 시 기본 응답
        output_dict = generate_fallback_response()
    
    # 출력 모델 변환
    recommended_actions = []
    for action in output_dict.get("recommended_actions", []):
        try:
            control_req = ControlRequest(
                action_type=ControlActionType(action.get("action_type")),
                target_id=action.get("target_id", "zone-1"),
                parameters=action.get("parameters", {}),
                priority=action.get("priority", 3),
                created_by="ai",
                llm_reason=action.get("reason")
            )
            recommended_actions.append(control_req)
        except Exception as e:
            print(f"제어 요청 생성 중 오류: {str(e)}")
    
    return LLMControlOutput(
        recommended_actions=recommended_actions,
        reasoning=output_dict.get("reasoning", "분석 데이터가 충분하지 않습니다."),
        risk_assessment=output_dict.get("risk_assessment", {"risk_level": "medium", "factors": []}),
        confidence_score=output_dict.get("confidence_score", 0.7)
    )

def generate_sample_response(input_data: LLMControlInput) -> Dict[str, Any]:
    """샘플 LLM 응답 생성 (실제 LLM 없을 때 테스트용)"""
    # 샘플 센서 데이터 확인
    sensor_data = input_data.sensor_data
    soil_moisture = sensor_data.get("soil_moisture", {}).get("average", 30)
    temperature = sensor_data.get("temperature", {}).get("average", 25)
    
    # 기본 응답 준비
    response = {
        "recommended_actions": [],
        "reasoning": "센서 데이터와 작물 상태 분석 결과에 따른 제어 계획입니다.",
        "risk_assessment": {
            "risk_level": "low",
            "factors": ["날씨 변화 가능성", "센서 정확도"]
        },
        "confidence_score": 0.85
    }
    
    # 수분이 낮으면 관수 추천
    if soil_moisture < 35:
        response["recommended_actions"].append({
            "action_type": "irrigation",
            "target_id": "zone-1",
            "parameters": {
                "duration": 900,  # 15분
                "intensity": 0.7,
                "water_volume": 2.5  # 리터/㎡
            },
            "priority": 2,
            "reason": "토양 수분이 35% 미만으로 최적 범위보다 낮습니다. 15분간 중간 강도의 관수가 필요합니다."
        })
        
        response["reasoning"] += "\n\n토양 수분이 현재 목표 범위(35-45%)보다 낮은 상태입니다. 수분 스트레스를 방지하기 위해 관수가 필요합니다."
    
    # 질소 부족 감지 시 비료 추천
    if input_data.crop_status.get("nutrient_deficiency", {}).get("nitrogen", False):
        response["recommended_actions"].append({
            "action_type": "fertilization",
            "target_id": "zone-2",
            "parameters": {
                "type": "nitrogen",
                "amount": 1.5,  # kg/ha
                "method": "drip"
            },
            "priority": 3,
            "reason": "질소 결핍 징후가 감지되었습니다. 식물 성장을 촉진하기 위해 질소 비료가 필요합니다."
        })
        
        response["reasoning"] += "\n\n작물 상태 분석 결과 질소 결핍 징후가 감지되었습니다. 현재 생육 단계에 맞는 질소 공급이 필요합니다."
    
    # 날씨가 더우면 환경 제어 추천
    if temperature > 28:
        response["recommended_actions"].append({
            "action_type": "environmental",
            "target_id": "greenhouse-1",
            "parameters": {
                "target_temperature": 26,
                "ventilation": True,
                "shade_level": 0.3
            },
            "priority": 2,
            "reason": "온도가 28°C 이상으로 최적 범위를 초과했습니다. 환기 및 차광이 필요합니다."
        })
        
        response["reasoning"] += "\n\n온도가 최적 범위(20-30°C)의 상단에 근접하고 있습니다. 과열을 방지하기 위한 환경 제어가 권장됩니다."
    
    return response

def generate_fallback_response() -> Dict[str, Any]:
    """LLM 오류 시 폴백 응답 생성"""
    return {
        "recommended_actions": [
            {
                "action_type": "irrigation",
                "target_id": "zone-1",
                "parameters": {"duration": 600, "intensity": 0.5},
                "priority": 3,
                "reason": "기본 관수 일정에 따른 유지 관리입니다."
            }
        ],
        "reasoning": "센서 또는 분석 시스템 오류로 인해 제한된 데이터로 결정했습니다. 기본 유지 관리 절차를 권장합니다.",
        "risk_assessment": {
            "risk_level": "medium",
            "factors": ["제한된 데이터", "시스템 오류"]
        },
        "confidence_score": 0.4
    } 