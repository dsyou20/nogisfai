"""
AI 제어 시스템 데이터 모델
"""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class ControlActionType(str, Enum):
    """제어 동작 유형"""
    IRRIGATION = "irrigation"  # 관수
    FERTILIZATION = "fertilization"  # 비료
    PEST_CONTROL = "pest_control"  # 방제
    ENVIRONMENTAL = "environmental"  # 환경 제어
    MANUAL = "manual"  # 수동 제어

class ControlStatus(str, Enum):
    """제어 상태"""
    PENDING = "pending"  # 대기 중
    EXECUTING = "executing"  # 실행 중
    COMPLETED = "completed"  # 완료됨
    FAILED = "failed"  # 실패함
    CANCELLED = "cancelled"  # 취소됨

class ControlAction(BaseModel):
    """제어 동작 모델"""
    action_id: str = Field(..., description="제어 동작 ID")
    action_type: ControlActionType = Field(..., description="제어 동작 유형")
    target_id: str = Field(..., description="제어 대상 ID (구역, 장비 등)")
    parameters: Dict[str, Any] = Field(..., description="제어 매개변수")
    scheduled_time: Optional[datetime] = Field(None, description="예약 실행 시간")
    duration: Optional[int] = Field(None, description="지속 시간(초)")
    priority: int = Field(3, ge=1, le=5, description="우선순위 (1:긴급, 5:낮음)")
    status: ControlStatus = Field(ControlStatus.PENDING, description="제어 상태")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    started_at: Optional[datetime] = Field(None, description="시작 시간")
    completed_at: Optional[datetime] = Field(None, description="완료 시간")
    created_by: str = Field(..., description="생성자 (user, system, ai)")
    llm_reason: Optional[str] = Field(None, description="LLM의 제어 판단 이유")

class ControlRequest(BaseModel):
    """제어 요청 모델"""
    action_type: ControlActionType
    target_id: str
    parameters: Dict[str, Any]
    scheduled_time: Optional[datetime] = None
    duration: Optional[int] = None
    priority: int = 3
    created_by: str = "user"
    llm_reason: Optional[str] = None

class AutoControlRule(BaseModel):
    """자동 제어 규칙 모델"""
    rule_id: str = Field(..., description="규칙 ID")
    name: str = Field(..., description="규칙 이름")
    description: Optional[str] = Field(None, description="규칙 설명")
    action_type: ControlActionType = Field(..., description="제어 동작 유형")
    target_ids: List[str] = Field(..., description="제어 대상 ID 목록")
    conditions: List[Dict[str, Any]] = Field(..., description="조건 목록")
    parameters: Dict[str, Any] = Field(..., description="제어 매개변수")
    enabled: bool = Field(True, description="활성화 여부")
    priority: int = Field(3, description="우선순위")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: Optional[datetime] = Field(None, description="업데이트 시간")

class ControlHistory(BaseModel):
    """제어 이력 모델"""
    start_date: datetime = Field(..., description="시작 날짜")
    end_date: datetime = Field(..., description="종료 날짜")
    action_type: Optional[ControlActionType] = Field(None, description="제어 동작 유형으로 필터링")
    target_id: Optional[str] = Field(None, description="제어 대상 ID로 필터링")
    status: Optional[ControlStatus] = Field(None, description="제어 상태로 필터링")
    created_by: Optional[str] = Field(None, description="생성자로 필터링")

class LLMControlInput(BaseModel):
    """LLM에 제공되는 제어 판단 입력 모델"""
    sensor_data: Dict[str, Any] = Field(..., description="현재 센서 데이터")
    crop_status: Dict[str, Any] = Field(..., description="작물 상태 데이터")
    historical_trends: Dict[str, Any] = Field(..., description="과거 데이터 추세")
    weather_forecast: Optional[Dict[str, Any]] = Field(None, description="날씨 예보")
    previous_actions: List[Dict[str, Any]] = Field([], description="이전 제어 동작")
    system_constraints: Dict[str, Any] = Field(..., description="시스템 제약 조건")

class LLMControlOutput(BaseModel):
    """LLM의 제어 판단 출력 모델"""
    recommended_actions: List[ControlRequest] = Field(..., description="추천 제어 동작 목록")
    reasoning: str = Field(..., description="추천 이유 설명")
    risk_assessment: Dict[str, Any] = Field(..., description="위험 평가")
    confidence_score: float = Field(..., ge=0, le=1, description="판단 신뢰도 점수") 