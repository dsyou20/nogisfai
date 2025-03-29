"""
센서 데이터 API 라우터
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.models.sensor import SensorData, SensorReading, SensorSummary, SensorAlert, SensorHistory
from app.db.database import db

router = APIRouter()

@router.post("/readings", response_model=dict)
async def create_sensor_readings(data: SensorData):
    """
    새로운 센서 측정값을 저장합니다.
    """
    try:
        # 실제로는 데이터베이스에 저장
        return {"message": f"{len(data.readings)}개의 센서 측정값이 저장되었습니다.", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"센서 데이터 저장 중 오류 발생: {str(e)}")

@router.get("/readings", response_model=List[SensorReading])
async def get_sensor_readings(
    sensor_type: Optional[str] = Query(None, description="센서 유형으로 필터링"),
    location: Optional[str] = Query(None, description="위치로 필터링"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit: int = Query(100, ge=1, le=1000, description="반환할 최대 레코드 수")
):
    """
    센서 측정값을 조회합니다.
    """
    # 예시 데이터 생성 (실제로는 DB에서 가져옴)
    end = end_time or datetime.now()
    start = start_time or (end - timedelta(hours=24))
    
    # 샘플 데이터 생성
    readings = []
    for i in range(min(limit, 10)):  # 테스트용으로 최대 10개만 생성
        reading = SensorReading(
            timestamp=start + timedelta(hours=i*2),
            sensor_id=f"sensor-{i+1}",
            sensor_type=sensor_type or ("온도" if i % 3 == 0 else "습도" if i % 3 == 1 else "조도"),
            value=20 + (i % 5),
            unit="°C" if (sensor_type or "온도") == "온도" else "%" if (sensor_type or "습도") == "습도" else "lux",
            location=location or f"A구역-{i//3+1}행-{i%3+1}열",
            battery_level=80 - (i*3 % 20),
            status="active" if i % 5 != 0 else "warning"
        )
        readings.append(reading)
    
    return readings

@router.get("/summary", response_model=List[SensorSummary])
async def get_sensor_summary(
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    section_id: Optional[str] = Query(None, description="구역 ID")
):
    """
    센서 데이터 요약 정보를 반환합니다.
    """
    # 샘플 데이터 생성
    summaries = [
        SensorSummary(
            sensor_type="온도",
            avg_value=23.5,
            min_value=18.2,
            max_value=28.7,
            unit="°C",
            warning_count=2,
            error_count=0
        ),
        SensorSummary(
            sensor_type="습도",
            avg_value=65.3,
            min_value=52.1,
            max_value=78.9,
            unit="%",
            warning_count=1,
            error_count=0
        ),
        SensorSummary(
            sensor_type="조도",
            avg_value=15200,
            min_value=800,
            max_value=35000,
            unit="lux",
            warning_count=0,
            error_count=0
        ),
        SensorSummary(
            sensor_type="토양수분",
            avg_value=42.7,
            min_value=35.2,
            max_value=55.8,
            unit="%",
            warning_count=3,
            error_count=1
        )
    ]
    
    return summaries

@router.get("/alerts", response_model=List[SensorAlert])
async def get_sensor_alerts(
    status: Optional[str] = Query(None, description="경고 상태로 필터링 (active, acknowledged, resolved)"),
    sensor_type: Optional[str] = Query(None, description="센서 유형으로 필터링"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit: int = Query(50, ge=1, le=500, description="반환할 최대 레코드 수")
):
    """
    센서 경고 정보를 반환합니다.
    """
    # 샘플 데이터 생성
    alerts = []
    current_time = datetime.now()
    alert_types = ["high", "low", "offline"]
    alert_statuses = ["active", "acknowledged", "resolved"]
    
    for i in range(min(5, limit)):
        alert_status = status or alert_statuses[i % 3]
        alert_type = alert_types[i % 3]
        sensor_t = sensor_type or ("온도" if i % 4 == 0 else "습도" if i % 4 == 1 else "조도" if i % 4 == 2 else "토양수분")
        
        alert = SensorAlert(
            alert_id=str(uuid.uuid4()),
            timestamp=current_time - timedelta(hours=i*4),
            sensor_id=f"sensor-{i+1}",
            sensor_type=sensor_t,
            alert_type=alert_type,
            value=30 + i if alert_type == "high" else 10 - i if alert_type == "low" else 0,
            threshold=28 if alert_type == "high" else 15 if alert_type == "low" else 0,
            status=alert_status,
            message=f"{sensor_t} {'높음' if alert_type == 'high' else '낮음' if alert_type == 'low' else '오프라인'} 경고"
        )
        
        alerts.append(alert)
    
    return alerts

@router.get("/history", response_model=dict)
async def get_sensor_history(query: SensorHistory = Depends()):
    """
    특정 기간 동안의 센서 데이터 이력을 반환합니다.
    """
    # 샘플 차트 데이터 생성
    labels = []
    temperature_data = []
    humidity_data = []
    
    current = query.start_date
    step = timedelta(hours=1) if query.interval == "hour" else timedelta(days=1)
    
    while current <= query.end_date:
        labels.append(current.isoformat())
        # 약간의 변동을 주는 샘플 데이터
        import random
        temperature_data.append(round(22 + random.uniform(-3, 3), 1))
        humidity_data.append(round(60 + random.uniform(-10, 10), 1))
        current += step
    
    return {
        "labels": labels,
        "datasets": [
            {
                "label": "온도 (°C)",
                "data": temperature_data,
                "borderColor": "rgba(255, 99, 132, 1)",
                "backgroundColor": "rgba(255, 99, 132, 0.2)"
            },
            {
                "label": "습도 (%)",
                "data": humidity_data,
                "borderColor": "rgba(54, 162, 235, 1)",
                "backgroundColor": "rgba(54, 162, 235, 0.2)"
            }
        ]
    } 