"""
센서 데이터 모델 정의
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

class SensorReading(BaseModel):
    """개별 센서 측정값 모델"""
    timestamp: datetime = Field(..., description="측정 시간")
    sensor_id: str = Field(..., description="센서 ID")
    sensor_type: str = Field(..., description="센서 유형 (온도, 습도, 조도 등)")
    value: float = Field(..., description="측정값")
    unit: str = Field(..., description="측정 단위 (°C, %, lux 등)")
    location: str = Field(..., description="센서 위치 (구역, 행, 열 등)")
    battery_level: Optional[float] = Field(None, description="센서 배터리 레벨 (%)")
    status: str = Field("active", description="센서 상태 (active, warning, error)")
    
class SensorData(BaseModel):
    """여러 센서 측정값을 포함하는 모델"""
    farm_id: str = Field(..., description="농장 ID")
    section_id: str = Field(..., description="구역 ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="데이터 수집 시간")
    readings: List[SensorReading] = Field(..., description="센서 측정값 목록")
    
class SensorSummary(BaseModel):
    """센서 측정값 요약 모델"""
    sensor_type: str = Field(..., description="센서 유형")
    avg_value: float = Field(..., description="평균값")
    min_value: float = Field(..., description="최소값") 
    max_value: float = Field(..., description="최대값")
    unit: str = Field(..., description="측정 단위")
    warning_count: int = Field(0, description="경고 발생 수")
    error_count: int = Field(0, description="오류 발생 수")
    
class SensorAlert(BaseModel):
    """센서 경고 모델"""
    alert_id: str = Field(..., description="경고 ID")
    timestamp: datetime = Field(..., description="경고 발생 시간")
    sensor_id: str = Field(..., description="센서 ID")
    sensor_type: str = Field(..., description="센서 유형")
    alert_type: str = Field(..., description="경고 유형 (low, high, offline 등)")
    value: float = Field(..., description="측정값")
    threshold: float = Field(..., description="임계값")
    status: str = Field("active", description="경고 상태 (active, acknowledged, resolved)")
    message: str = Field(..., description="경고 메시지")
    
class SensorHistory(BaseModel):
    """센서 이력 쿼리 모델"""
    sensor_id: Optional[str] = Field(None, description="센서 ID")
    sensor_type: Optional[str] = Field(None, description="센서 유형")
    start_date: datetime = Field(..., description="시작 날짜")
    end_date: datetime = Field(..., description="종료 날짜")
    interval: str = Field("hour", description="집계 간격 (raw, hour, day, week, month)")
    location: Optional[str] = Field(None, description="센서 위치") 