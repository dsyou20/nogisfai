"""
작물 분석 관련 API 엔드포인트
"""
from fastapi import APIRouter, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# 라우터 정의
router = APIRouter()

# 작물 분석 데이터 조회 엔드포인트
@router.get("/data")
async def get_crop_analysis(
    crop_id: Optional[str] = Query(None, description="작물 ID"),
    region: Optional[str] = Query(None, description="지역"),
    period: Optional[str] = Query("1month", description="기간 (1week, 1month, 3month, 6month)")
):
    """작물 분석 데이터 조회 API"""
    # 가상의 응답 데이터 생성
    now = datetime.now()
    
    # 기간에 따른 데이터 포인트 수 결정
    if period == "1week":
        data_points = 7
    elif period == "1month":
        data_points = 30
    elif period == "3month":
        data_points = 90
    else:  # 6month
        data_points = 180
    
    # 샘플 데이터
    return {
        "success": True,
        "data": {
            "crop_name": "배추" if crop_id is None else f"작물-{crop_id}",
            "region": region or "김제지구",
            "period": period,
            "growth_timeline": [
                {
                    "date": (now - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "growth_stage": get_growth_stage(i, data_points),
                    "ndvi": 0.3 + (0.5 * (1 - i/data_points)),
                    "height": 10 + (40 * (1 - i/data_points)),
                    "notes": f"생육 상태 양호 ({data_points-i}일차)"
                } for i in range(min(10, data_points))
            ]
        }
    }

# 작물 목록 조회 엔드포인트
@router.get("/list")
async def get_crop_list():
    """작물 목록 조회 API"""
    return {
        "success": True,
        "data": [
            {"id": "crop1", "name": "배추", "region": "김제지구"},
            {"id": "crop2", "name": "무", "region": "태안지구"},
            {"id": "crop3", "name": "콩", "region": "밀양지구"},
            {"id": "crop4", "name": "고추", "region": "김제지구"},
            {"id": "crop5", "name": "참외", "region": "밀양지구"}
        ]
    }

def get_growth_stage(day_offset, total_days):
    """생육 단계 계산 함수"""
    progress = 1 - (day_offset / total_days)
    
    if progress < 0.2:
        return "수확기"
    elif progress < 0.4:
        return "결실기"
    elif progress < 0.6:
        return "개화기"
    elif progress < 0.8:
        return "영양생장기"
    else:
        return "발아기" 