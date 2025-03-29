"""
AI 챗봇 API 라우터
"""
from fastapi import APIRouter, HTTPException, Body, Query, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

router = APIRouter()

@router.post("/chat", response_model=Dict[str, Any])
async def chat_with_bot(
    message: Dict[str, Any] = Body(..., 
        example={
            "user_id": "user-1",
            "session_id": "session-123", 
            "message": "최근 콩 생육 상태는 어떤가요?", 
            "farm_id": "farm-1"
        }
    )
):
    """
    AI 챗봇과 대화하기 위한 엔드포인트
    """
    # 요청된 메시지에서 정보 추출
    user_id = message.get("user_id", "anonymous")
    session_id = message.get("session_id", str(uuid.uuid4()))
    user_message = message.get("message", "")
    farm_id = message.get("farm_id", "farm-1")
    
    # 이 부분에서 실제로는 LLM 호출이 이루어짐
    # 여기서는 샘플 응답 반환
    response_message = generate_sample_response(user_message, farm_id)
    
    return {
        "response_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "request": user_message,
        "response": response_message,
        "confidence": 0.92,
        "sources": [
            {
                "type": "sensor_data",
                "description": "최근 7일간 센서 데이터",
                "relevance": "high"
            },
            {
                "type": "crop_analysis",
                "description": "최근 작물 상태 분석",
                "relevance": "high"
            }
        ]
    }

@router.get("/knowledge", response_model=Dict[str, Any])
async def get_knowledge_base(
    query: Optional[str] = Query(None, description="검색 쿼리"),
    farm_id: Optional[str] = Query(None, description="농장 ID"),
    category: Optional[str] = Query(None, description="지식 카테고리")
):
    """
    농업 지식 베이스를 검색합니다.
    """
    # 샘플 데이터
    return {
        "query": query or "",
        "farm_id": farm_id or "farm-1",
        "category": category or "all",
        "results": [
            {
                "id": "kb-1",
                "title": "콩 생육 최적 환경 조건",
                "category": "재배 관리",
                "content": "콩은 생육 단계에 따라 다양한 환경 조건이 필요합니다. 발아기에는 토양 온도 20-30°C, 토양 수분 60-70%가 적합합니다. 영양생장기에는...",
                "relevance_score": 0.95,
                "source": "농촌진흥청 콩 재배 지침서"
            },
            {
                "id": "kb-2",
                "title": "콩 흰가루병 증상 및 대처 방법",
                "category": "병해충 관리",
                "content": "흰가루병은 초기에 잎 표면에 작은 흰색 반점으로 나타납니다. 진행되면 흰색 가루 같은 포자로 덮히게 됩니다. 발견 즉시 이병 부위를 제거하고...",
                "relevance_score": 0.82,
                "source": "스마트팜 병해충 가이드"
            }
        ],
        "total_results": 2
    }

@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_chat_session(
    session_id: str
):
    """
    특정 채팅 세션의 대화 기록을 반환합니다.
    """
    # 샘플 데이터
    now = datetime.now()
    
    return {
        "session_id": session_id,
        "user_id": "user-1",
        "farm_id": "farm-1",
        "start_time": (now - timedelta(minutes=30)).isoformat(),
        "last_active": now.isoformat(),
        "conversations": [
            {
                "message_id": "msg-1",
                "timestamp": (now - timedelta(minutes=30)).isoformat(),
                "role": "user",
                "content": "최근 콩 생육 상태는 어떤가요?"
            },
            {
                "message_id": "msg-2",
                "timestamp": (now - timedelta(minutes=29)).isoformat(),
                "role": "assistant",
                "content": "현재 귀하의 농장 콩은 개화기 중반에 있으며, 전반적인 생육 상태는 양호합니다. 평균 초장은 45.3cm로 정상 범위이며, 개화율은 75.5%입니다. 다만, 질소 함량이 14.2ppm으로 약간 낮은 편이니 추가 시비를 고려해보세요."
            },
            {
                "message_id": "msg-3",
                "timestamp": (now - timedelta(minutes=25)).isoformat(),
                "role": "user",
                "content": "질소 비료는 얼마나 추가하는 것이 좋을까요?"
            },
            {
                "message_id": "msg-4",
                "timestamp": (now - timedelta(minutes=24)).isoformat(),
                "role": "assistant",
                "content": "현재 질소 함량이 14.2ppm이고 최적 범위는 15-20ppm입니다. 귀하의 농장 면적 2ha 기준으로 요소비료를 10-15kg 정도 추가 시비하시면 적정 수준에 도달할 것으로 예상됩니다. 가급적 이른 아침이나 저녁에 시비하시고, 시비 후 가볍게 관수하여 비료 효과를 높이세요."
            }
        ],
        "summary": {
            "topics": ["생육 상태", "비료 관리"],
            "actions_taken": ["비료 시비 권장"],
            "pending_queries": []
        }
    }

def generate_sample_response(user_message: str, farm_id: str) -> str:
    """
    사용자 메시지에 따른 샘플 응답을 생성합니다.
    """
    if "생육" in user_message or "상태" in user_message:
        return "현재 귀하의 농장 콩은 개화기 중반에 있으며, 전반적인 생육 상태는 양호합니다. 평균 초장은 45.3cm로 정상 범위이며, 개화율은 75.5%입니다. 다만, 질소 함량이 14.2ppm으로 약간 낮은 편이니 추가 시비를 고려해보세요."
    
    elif "비료" in user_message or "질소" in user_message:
        return "현재 질소 함량이 14.2ppm이고 최적 범위는 15-20ppm입니다. 귀하의 농장 면적 2ha 기준으로 요소비료를 10-15kg 정도 추가 시비하시면 적정 수준에 도달할 것으로 예상됩니다. 가급적 이른 아침이나 저녁에 시비하시고, 시비 후 가볍게 관수하여 비료 효과를 높이세요."
    
    elif "병해충" in user_message or "질병" in user_message:
        return "최근 농장 점검 결과, A구역에서 흰가루병 초기 증상이 발견되었습니다. 현재는 심각도가 낮고 발생 범위가 제한적이어서 즉각적인 조치는 필요하지 않습니다. 다만, 해당 구역을 면밀히 모니터링하고 있으며, 확산 징후가 보이면 즉시 알려드리겠습니다."
    
    elif "수확" in user_message or "예측" in user_message:
        return "현재 생육 상태와 기상 조건을 분석한 결과, 예상 수확량은 3.8톤/ha로 전년 대비 8.57% 증가할 것으로 예측됩니다. 예상 수확 시기는 약 45일 후입니다. 특히 올해는 기후 조건과 수분 관리가 긍정적으로 작용하고 있습니다."
    
    else:
        return "안녕하세요! 귀하의 스마트팜 어시스턴트입니다. 작물 상태, 병해충, 비료 관리, 수확 예측 등에 대해 질문해 주시면 자세히 답변해 드리겠습니다." 