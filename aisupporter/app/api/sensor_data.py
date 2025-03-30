"""
센서 데이터 관련 API 엔드포인트
"""
from fastapi import APIRouter, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# 라우터 정의
router = APIRouter()

# 기본 센서 데이터 조회 엔드포인트
@router.get("/data")
async def get_sensor_data(
    sensor_id: Optional[str] = Query(None, description="센서 ID"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)")
):
    """센서 데이터 조회 API"""
    # 가상의 응답 데이터 생성
    now = datetime.now()
    
    # 샘플 데이터
    return {
        "success": True,
        "data": [
            {
                "timestamp": (now - timedelta(hours=i)).isoformat(),
                "sensor_id": sensor_id or "sensor1",
                "temperature": 20 + (i % 10),
                "humidity": 50 + (i % 20)
            } for i in range(10)
        ],
        "params": {
            "sensor_id": sensor_id,
            "start_date": start_date,
            "end_date": end_date
        }
    }

# 센서 목록 조회 엔드포인트
@router.get("/list")
async def get_sensor_list():
    """센서 목록 조회 API"""
    return {
        "success": True,
        "data": [
            {"id": "sensor1", "name": "온습도센서 1", "type": "temperature"},
            {"id": "sensor2", "name": "온습도센서 2", "type": "temperature"},
            {"id": "sensor3", "name": "토양센서 1", "type": "soil"},
            {"id": "sensor4", "name": "토양센서 2", "type": "soil"},
            {"id": "sensor5", "name": "대기질센서", "type": "air"}
        ]
    } 