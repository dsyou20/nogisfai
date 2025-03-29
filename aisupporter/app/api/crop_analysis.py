"""
작물 분석 API 라우터
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

router = APIRouter()

@router.get("/status", response_model=Dict[str, Any])
async def get_crop_status(
    farm_id: Optional[str] = Query(None, description="농장 ID"),
    section_id: Optional[str] = Query(None, description="구역 ID")
):
    """
    현재 작물 상태 정보를 반환합니다.
    """
    # 샘플 데이터 생성
    return {
        "farm_id": farm_id or "farm-1",
        "section_id": section_id or "section-1",
        "crop_type": "콩",
        "growth_stage": "개화기",
        "health_status": "양호",
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "height": {
                "value": 45.3,
                "unit": "cm",
                "status": "normal"
            },
            "leaf_color": {
                "value": "짙은 녹색",
                "status": "normal"
            },
            "flowering_rate": {
                "value": 75.5,
                "unit": "%",
                "status": "normal"
            },
            "leaf_count": {
                "value": 18.2,
                "unit": "장/주",
                "status": "normal"
            }
        },
        "nutrition": {
            "nitrogen": {
                "value": 14.2,
                "unit": "ppm",
                "status": "slightly_low",
                "optimal_range": "15-20"
            },
            "phosphorus": {
                "value": 8.5,
                "unit": "ppm",
                "status": "normal",
                "optimal_range": "8-12"
            },
            "potassium": {
                "value": 150.3,
                "unit": "ppm",
                "status": "normal",
                "optimal_range": "140-200"
            },
            "trace_elements": {
                "status": "normal"
            }
        },
        "nutrient_deficiency": {
            "nitrogen": True,
            "phosphorus": False,
            "potassium": False
        }
    }

@router.get("/disease-detection", response_model=Dict[str, Any])
async def get_disease_detection(
    farm_id: Optional[str] = Query(None, description="농장 ID"),
    section_id: Optional[str] = Query(None, description="구역 ID")
):
    """
    작물 병해충 감지 결과를 반환합니다.
    """
    # 샘플 데이터
    return {
        "farm_id": farm_id or "farm-1",
        "section_id": section_id or "section-1",
        "timestamp": datetime.now().isoformat(),
        "detections": [
            {
                "id": str(uuid.uuid4()),
                "type": "disease",
                "name": "흰가루병",
                "confidence": 0.15,
                "severity": "low",
                "location": "A구역-2행-1열",
                "detection_time": (datetime.now() - timedelta(hours=2)).isoformat(),
                "status": "monitoring",
                "recommended_action": "현재는 처리 불필요, 모니터링 지속"
            }
        ],
        "summary": {
            "total_inspections": 24,
            "disease_detected": 1,
            "pest_detected": 0,
            "critical_issues": 0,
            "status": "healthy"
        }
    }

@router.get("/yield-prediction", response_model=Dict[str, Any])
async def get_yield_prediction(
    farm_id: Optional[str] = Query(None, description="농장 ID"),
    section_id: Optional[str] = Query(None, description="구역 ID")
):
    """
    수확량 예측 결과를 반환합니다.
    """
    # 샘플 데이터
    return {
        "farm_id": farm_id or "farm-1",
        "section_id": section_id or "section-1",
        "prediction_date": datetime.now().isoformat(),
        "harvest_date_estimated": (datetime.now() + timedelta(days=45)).isoformat(),
        "predicted_yield": {
            "value": 3.8,
            "unit": "톤/ha",
            "confidence_interval": [3.5, 4.1]
        },
        "comparison": {
            "previous_year": {
                "value": 3.5,
                "unit": "톤/ha",
                "change_percent": 8.57
            },
            "regional_average": {
                "value": 3.2,
                "unit": "톤/ha", 
                "change_percent": 18.75
            }
        },
        "factors": [
            {
                "name": "기후 조건",
                "impact": "positive",
                "contribution": 0.3
            },
            {
                "name": "수분 관리",
                "impact": "positive", 
                "contribution": 0.25
            },
            {
                "name": "영양 관리",
                "impact": "neutral",
                "contribution": 0.1
            }
        ]
    }

@router.get("/growth-analysis", response_model=Dict[str, Any])
async def get_growth_analysis(
    farm_id: Optional[str] = Query(None, description="농장 ID"),
    section_id: Optional[str] = Query(None, description="구역 ID"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜")
):
    """
    작물 생육 분석 결과를 반환합니다.
    """
    now = datetime.now()
    end = end_date or now
    start = start_date or (end - timedelta(days=30))
    
    # 샘플 데이터
    return {
        "farm_id": farm_id or "farm-1",
        "section_id": section_id or "section-1",
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat()
        },
        "growth_stages": [
            {
                "stage": "발아기",
                "start_date": (now - timedelta(days=60)).isoformat(),
                "end_date": (now - timedelta(days=50)).isoformat(),
                "duration_days": 10,
                "status": "completed",
                "performance": "optimal"
            },
            {
                "stage": "영양생장기",
                "start_date": (now - timedelta(days=50)).isoformat(),
                "end_date": (now - timedelta(days=25)).isoformat(),
                "duration_days": 25,
                "status": "completed",
                "performance": "optimal"
            },
            {
                "stage": "개화기",
                "start_date": (now - timedelta(days=25)).isoformat(),
                "end_date": (now + timedelta(days=10)).isoformat(),
                "duration_days": 35,
                "status": "in_progress",
                "current_day": 25,
                "progress_percent": 71.4,
                "performance": "optimal"
            }
        ],
        "growth_metrics": {
            "height_trend": [
                {"date": (now - timedelta(days=30)).isoformat(), "value": 20.5},
                {"date": (now - timedelta(days=20)).isoformat(), "value": 30.2},
                {"date": (now - timedelta(days=10)).isoformat(), "value": 38.7},
                {"date": now.isoformat(), "value": 45.3}
            ],
            "leaf_count_trend": [
                {"date": (now - timedelta(days=30)).isoformat(), "value": 8},
                {"date": (now - timedelta(days=20)).isoformat(), "value": 12},
                {"date": (now - timedelta(days=10)).isoformat(), "value": 15},
                {"date": now.isoformat(), "value": 18}
            ]
        }
    } 