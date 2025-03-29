"""
AI 제어 시스템 API 라우터
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import json

from app.models.control import (
    ControlAction, ControlRequest, AutoControlRule, ControlHistory,
    ControlActionType, ControlStatus, LLMControlInput, LLMControlOutput
)
from app.llm.control_agent import analyze_control_decision
from app.db.database import db

router = APIRouter()

@router.post("/actions", response_model=ControlAction)
async def create_control_action(request: ControlRequest):
    """
    새로운 제어 동작을 생성합니다.
    """
    action_id = f"action-{uuid.uuid4()}"
    action = ControlAction(
        action_id=action_id,
        action_type=request.action_type,
        target_id=request.target_id,
        parameters=request.parameters,
        scheduled_time=request.scheduled_time,
        duration=request.duration,
        priority=request.priority,
        created_by=request.created_by,
        llm_reason=request.llm_reason
    )
    
    # 실제로는 DB에 저장
    
    return action

@router.get("/actions", response_model=List[ControlAction])
async def get_control_actions(
    action_type: Optional[ControlActionType] = None,
    target_id: Optional[str] = None,
    status: Optional[ControlStatus] = None,
    created_by: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """
    제어 동작 목록을 조회합니다.
    """
    # 샘플 데이터 생성
    actions = []
    now = datetime.now()
    
    for i in range(min(10, limit)):
        action_status = status or (
            ControlStatus.COMPLETED if i < 4 else
            ControlStatus.EXECUTING if i == 4 else
            ControlStatus.PENDING if i < 7 else
            ControlStatus.FAILED
        )
        
        created_time = now - timedelta(hours=i*2)
        started_time = created_time + timedelta(minutes=5) if action_status != ControlStatus.PENDING else None
        completed_time = started_time + timedelta(minutes=20) if action_status == ControlStatus.COMPLETED else None
        
        action_created_by = created_by or ("ai" if i % 3 == 0 else "system" if i % 3 == 1 else "user")
        action_type_val = action_type or (
            ControlActionType.IRRIGATION if i % 4 == 0 else
            ControlActionType.FERTILIZATION if i % 4 == 1 else
            ControlActionType.PEST_CONTROL if i % 4 == 2 else
            ControlActionType.ENVIRONMENTAL
        )
        
        action = ControlAction(
            action_id=f"action-{uuid.uuid4()}",
            action_type=action_type_val,
            target_id=target_id or f"zone-{i % 3 + 1}",
            parameters={
                "level": i % 5 + 1,
                "mode": "automatic",
                "intensity": 0.7 + (i % 3) * 0.1
            },
            scheduled_time=now + timedelta(hours=i) if action_status == ControlStatus.PENDING else None,
            duration=600 + i * 60,  # 10-20분
            priority=i % 5 + 1,
            status=action_status,
            created_at=created_time,
            started_at=started_time,
            completed_at=completed_time,
            created_by=action_created_by,
            llm_reason="토양 수분이 최적 범위보다 낮아 관수가 필요합니다." if action_type_val == ControlActionType.IRRIGATION else
                      "질소 수치가 낮아 비료 공급이 필요합니다." if action_type_val == ControlActionType.FERTILIZATION else
                      "초기 해충 발생이 감지되어 예방적 방제가 필요합니다." if action_type_val == ControlActionType.PEST_CONTROL else
                      "온도가 최적 범위를 벗어나 환경 제어가 필요합니다."
        )
        
        actions.append(action)
    
    return actions

@router.get("/actions/{action_id}", response_model=ControlAction)
async def get_control_action(action_id: str):
    """
    특정 제어 동작의 상세 정보를 조회합니다.
    """
    # 실제로는 DB에서 조회
    now = datetime.now()
    
    # 샘플 데이터 생성
    action = ControlAction(
        action_id=action_id,
        action_type=ControlActionType.IRRIGATION,
        target_id="zone-1",
        parameters={
            "level": 3,
            "mode": "automatic",
            "intensity": 0.8,
            "duration_minutes": 15
        },
        duration=900,  # 15분
        priority=2,
        status=ControlStatus.COMPLETED,
        created_at=now - timedelta(hours=1),
        started_at=now - timedelta(minutes=50),
        completed_at=now - timedelta(minutes=35),
        created_by="ai",
        llm_reason="""
        토양 수분 센서 데이터는 현재 28%로, 콩 생육 최적 수분 범위(35-45%)보다 낮습니다.
        지난 3일간의 수분 추세를 분석한 결과, 지속적인 감소 패턴이 확인되었으며,
        기상 예보에 따르면 향후 48시간 내 강수 확률이 10% 미만입니다.
        따라서 수분 스트레스를 방지하기 위해 15분간 중간 강도의 관수가 필요합니다.
        """
    )
    
    return action

@router.post("/actions/{action_id}/execute", response_model=ControlAction)
async def execute_control_action(action_id: str):
    """
    대기 중인 제어 동작을 즉시 실행합니다.
    """
    # 실제로는 DB에서 조회 후 상태 업데이트
    now = datetime.now()
    
    # 샘플 데이터로 실행 중 상태의 액션 반환
    action = ControlAction(
        action_id=action_id,
        action_type=ControlActionType.IRRIGATION,
        target_id="zone-1",
        parameters={
            "level": 3,
            "mode": "automatic",
            "intensity": 0.8
        },
        duration=900,  # 15분
        priority=2,
        status=ControlStatus.EXECUTING,  # 실행 중으로 상태 변경
        created_at=now - timedelta(minutes=5),
        started_at=now,  # 방금 시작됨
        completed_at=None,
        created_by="user",
        llm_reason=None
    )
    
    return action

@router.post("/ai-decision", response_model=LLMControlOutput)
async def get_ai_decision(input_data: LLMControlInput):
    """
    현재 농장 상태를 기반으로 LLM을 통해 제어 결정을 얻습니다.
    """
    try:
        # LLM 제어 에이전트를 호출하여 결정 분석
        decision = analyze_control_decision(input_data)
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 제어 결정 중 오류 발생: {str(e)}")

@router.get("/rules", response_model=List[AutoControlRule])
async def get_auto_control_rules(
    action_type: Optional[ControlActionType] = None,
    target_id: Optional[str] = None,
    enabled: Optional[bool] = None
):
    """
    자동 제어 규칙 목록을 조회합니다.
    """
    # 샘플 데이터 생성
    rules = []
    
    # 관수 규칙
    irrigation_rule = AutoControlRule(
        rule_id="rule-1",
        name="저수분 자동 관수",
        description="토양 수분이 30% 이하로 떨어질 경우 자동 관수",
        action_type=ControlActionType.IRRIGATION,
        target_ids=["zone-1", "zone-2"],
        conditions=[
            {"sensor_type": "soil_moisture", "operator": "less_than", "value": 30},
            {"sensor_type": "temperature", "operator": "greater_than", "value": 15}
        ],
        parameters={"level": 2, "duration": 600},
        enabled=True,
        priority=2,
        created_at=datetime.now() - timedelta(days=10),
        updated_at=datetime.now() - timedelta(days=2)
    )
    rules.append(irrigation_rule)
    
    # 방제 규칙
    pest_control_rule = AutoControlRule(
        rule_id="rule-2",
        name="병해충 자동 방제",
        description="잎 이미지에서 병해충이 감지될 경우 자동 방제",
        action_type=ControlActionType.PEST_CONTROL,
        target_ids=["zone-1", "zone-2", "zone-3"],
        conditions=[
            {"analysis_type": "leaf_image", "disease_detected": True, "confidence": 0.75}
        ],
        parameters={"spray_type": "organic", "intensity": 0.6, "duration": 300},
        enabled=True,
        priority=1,
        created_at=datetime.now() - timedelta(days=15),
        updated_at=datetime.now() - timedelta(days=5)
    )
    rules.append(pest_control_rule)
    
    # 비료 공급 규칙
    fertilizer_rule = AutoControlRule(
        rule_id="rule-3",
        name="질소 부족 비료 공급",
        description="토양 분석에서 질소가 부족할 경우 자동 비료 공급",
        action_type=ControlActionType.FERTILIZATION,
        target_ids=["zone-3"],
        conditions=[
            {"analysis_type": "soil_nutrient", "nutrient": "nitrogen", "operator": "less_than", "value": 15},
            {"crop_growth_stage": "vegetative"}
        ],
        parameters={"fertilizer_type": "nitrogen_rich", "amount": 2.5},
        enabled=True,
        priority=3,
        created_at=datetime.now() - timedelta(days=20),
        updated_at=None
    )
    rules.append(fertilizer_rule)
    
    # 필터링 적용
    if action_type:
        rules = [rule for rule in rules if rule.action_type == action_type]
    if target_id:
        rules = [rule for rule in rules if target_id in rule.target_ids]
    if enabled is not None:
        rules = [rule for rule in rules if rule.enabled == enabled]
    
    return rules

@router.get("/history", response_model=dict)
async def get_control_history(query: ControlHistory = Depends()):
    """
    제어 동작 이력을 조회합니다.
    """
    # 샘플 차트 데이터 생성
    date_range = []
    irrigation_data = []
    fertilization_data = []
    pest_control_data = []
    
    current = query.start_date
    step = timedelta(days=1)
    
    while current <= query.end_date:
        date_range.append(current.strftime("%Y-%m-%d"))
        
        # 각 날짜별 제어 동작 횟수
        import random
        irrigation_count = random.randint(0, 3 if current.weekday() < 5 else 1)
        fertilization_count = 1 if current.day % 7 == 0 else 0
        pest_control_count = 1 if current.day % 10 == 0 else 0
        
        irrigation_data.append(irrigation_count)
        fertilization_data.append(fertilization_count)
        pest_control_data.append(pest_control_count)
        
        current += step
    
    return {
        "labels": date_range,
        "datasets": [
            {
                "label": "관수",
                "data": irrigation_data,
                "backgroundColor": "rgba(54, 162, 235, 0.5)"
            },
            {
                "label": "비료",
                "data": fertilization_data,
                "backgroundColor": "rgba(153, 102, 255, 0.5)"
            },
            {
                "label": "방제",
                "data": pest_control_data,
                "backgroundColor": "rgba(255, 99, 132, 0.5)"
            }
        ]
    } 