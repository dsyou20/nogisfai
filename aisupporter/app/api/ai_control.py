"""
AI 제어 관련 API 엔드포인트
"""
from fastapi import APIRouter, Query, Body, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random

# 라우터 정의
router = APIRouter()

# AI 제어 상태 조회 엔드포인트
@router.get("/status")
async def get_control_status(
    zone_id: Optional[str] = Query(None, description="구역 ID")
):
    """AI 제어 상태 조회 API"""
    zones = ["A", "B", "C", "D"]
    zone = zone_id or random.choice(zones)
    
    # 가상의 제어 상태 생성
    return {
        "success": True,
        "data": {
            "zone_id": zone,
            "irrigation": {
                "status": random.choice(["active", "inactive", "scheduled"]),
                "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "next_scheduled": (datetime.now() + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
                "water_used_today": round(random.uniform(10, 50), 1)
            },
            "fertilization": {
                "status": random.choice(["active", "inactive", "scheduled"]),
                "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "next_scheduled": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                "balance": {"N": 50, "P": 30, "K": 40}
            },
            "pest_control": {
                "status": random.choice(["active", "inactive", "scheduled"]),
                "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "next_scheduled": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
                "threats_detected": random.randint(0, 3)
            }
        }
    }

# 제어 명령 실행 엔드포인트
@router.post("/execute")
async def execute_control(
    command: Dict[str, Any] = Body(..., description="제어 명령")
):
    """제어 명령 실행 API"""
    if "action" not in command or "zone_id" not in command:
        raise HTTPException(status_code=400, detail="필수 필드 누락: action, zone_id")
    
    # 명령 검증
    valid_actions = ["irrigation", "fertilization", "pest_control"]
    if command["action"] not in valid_actions:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 action. 유효한 값: {valid_actions}")
    
    # 가상의 응답
    return {
        "success": True,
        "data": {
            "execution_id": f"exec-{random.randint(1000, 9999)}",
            "status": "initiated",
            "message": f"{command['zone_id']} 구역에 {command['action']} 명령 실행 중",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estimated_completion": (datetime.now() + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
        }
    }

# 제어 이력 조회 엔드포인트
@router.get("/history")
async def get_control_history(
    zone_id: Optional[str] = Query(None, description="구역 ID"),
    action: Optional[str] = Query(None, description="액션 유형"),
    days: int = Query(7, description="조회 기간(일)")
):
    """제어 이력 조회 API"""
    now = datetime.now()
    actions = ["irrigation", "fertilization", "pest_control"]
    zones = ["A", "B", "C", "D"]
    
    # 필터링된 액션과 구역
    filtered_actions = [action] if action in actions else actions
    filtered_zones = [zone_id] if zone_id in zones else zones
    
    # 가상의 이력 데이터 생성
    history = []
    for i in range(min(20, days * 3)):
        history.append({
            "execution_id": f"exec-{random.randint(1000, 9999)}",
            "action": random.choice(filtered_actions),
            "zone_id": random.choice(filtered_zones),
            "status": random.choice(["completed", "completed", "failed"]),
            "timestamp": (now - timedelta(hours=i*4)).strftime("%Y-%m-%d %H:%M:%S"),
            "duration_minutes": random.randint(10, 60),
            "result": random.choice(["success", "success", "partial", "failed"])
        })
    
    return {
        "success": True,
        "data": history,
        "params": {
            "zone_id": zone_id,
            "action": action,
            "days": days
        }
    } 