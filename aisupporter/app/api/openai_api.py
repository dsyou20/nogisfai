"""
OpenAI API 통합 모듈
파인튜닝, 챗봇 및 기타 AI 기능을 위한 OpenAI API 관련 기능을 처리합니다.
"""

import os
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
import httpx
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.knowledge import KnowledgeItemCreate, KnowledgeItemList, KnowledgeItem

# .env 파일 로드
load_dotenv()

# API 라우터 설정
router = APIRouter()

# API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    print("경고: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. API 호출이 실패할 수 있습니다.")

# 기본 API 헤더
def get_headers():
    return {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

# 모델
class FineTuningRequest(BaseModel):
    model: str
    training_file: str
    suffix: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    validation_file: Optional[str] = None

class ExtractedPage(BaseModel):
    page_num: int
    text: str

class GenerationPrompt(BaseModel):
    model: str
    prompt_template: str
    pages: List[ExtractedPage]
    pairs_per_page: int
    include_context: bool = True
    save_to_database: bool = True  # 데이터베이스 저장 옵션 추가
    category_id: Optional[int] = None  # 카테고리 ID 추가

# PDF에서 추출한 텍스트로 파인튜닝 데이터 생성
@router.post("/generate-training-data", response_model=Dict[str, Any])
async def generate_training_data(prompt: GenerationPrompt, db: Session = Depends(get_db)):
    all_data = []
    db_items = []
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 각 페이지에 대해 처리
            for page in prompt.pages:
                # 컨텍스트 포함 여부에 따라 프롬프트 구성
                context = page.text
                full_prompt = f"{prompt.prompt_template}\n\n컨텍스트: {context}" if prompt.include_context else prompt.prompt_template
                
                # OpenAI API 호출
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=get_headers(),
                    json={
                        "model": prompt.model,
                        "messages": [
                            {"role": "system", "content": "당신은 농업 분야의 전문 지식을 가진 AI 어시스턴트입니다. 주어진 컨텍스트를 바탕으로 질문-답변 쌍을 생성합니다."},
                            {"role": "user", "content": full_prompt}
                        ],
                        "temperature": 0.7
                    }
                )
                
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail=f"OpenAI API 오류: {response.text}")
                
                result = response.json()
                generated_text = result["choices"][0]["message"]["content"]
                
                # 생성된 텍스트를 JSONL 형식으로 파싱
                try:
                    # 간단한 파싱 예시 (실제로는 더 강건한 파싱 로직 필요)
                    pairs = parse_qa_pairs(generated_text, prompt.pairs_per_page)
                    all_data.extend(pairs)
                    
                    # 데이터베이스에 저장 (옵션이 활성화된 경우)
                    if prompt.save_to_database:
                        for pair in pairs:
                            # 질문과 답변 추출
                            question = pair["messages"][0]["content"]
                            answer = pair["messages"][1]["content"]
                            
                            # 지식 항목 생성
                            item_create = KnowledgeItemCreate(
                                question=question,
                                answer=answer,
                                source=f"Page {page.page_num}",
                                source_page=page.page_num,
                                category_id=prompt.category_id,
                                confidence=0.85,  # 기본 신뢰도 설정
                                tags=["AI생성", f"페이지{page.page_num}"]  # 기본 태그 설정
                            )
                            
                            # 저장소를 통해 데이터베이스에 저장
                            db_item = KnowledgeRepository.create_knowledge_item(
                                db=db,
                                question=item_create.question,
                                answer=item_create.answer,
                                source=item_create.source,
                                source_page=item_create.source_page,
                                category_id=item_create.category_id,
                                tags=item_create.tags,
                                confidence=item_create.confidence
                            )
                            
                            db_items.append(db_item)
                    
                except Exception as e:
                    raise HTTPException(status_code=422, detail=f"응답 파싱 오류: {str(e)}")
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"OpenAI API 요청 실패: {str(e)}")
    
    # 저장된 항목들의 ID 목록
    saved_item_ids = [item.id for item in db_items] if db_items else []
    
    return {
        "data": all_data,
        "count": len(all_data),
        "saved_to_database": prompt.save_to_database,
        "saved_items": saved_item_ids,
        "category_id": prompt.category_id
    }

# 파일 업로드 (파인튜닝용)
@router.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    purpose: str = Form("fine-tune")
):
    try:
        content = await file.read()
        
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, content, file.content_type)}
            data = {"purpose": purpose}
            
            response = await client.post(
                "https://api.openai.com/v1/files",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                files=files,
                data=data
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"OpenAI API 오류: {response.text}"
                )
            
            return response.json()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 업로드 오류: {str(e)}")

# 파인튜닝 작업 생성
@router.post("/create-fine-tuning-job")
async def create_fine_tuning_job(request: FineTuningRequest, background_tasks: BackgroundTasks):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/fine_tuning/jobs",
                headers=get_headers(),
                json=request.dict(exclude_none=True)
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"OpenAI API 오류: {response.text}"
                )
            
            job_data = response.json()
            
            # 백그라운드에서 작업 상태 모니터링 (실제 구현에서는 더 강건한 방법으로)
            background_tasks.add_task(monitor_fine_tuning_job, job_data["id"])
            
            return job_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파인튜닝 작업 생성 오류: {str(e)}")

# 파인튜닝 작업 목록 조회
@router.get("/fine-tuning-jobs")
async def list_fine_tuning_jobs(limit: int = 10):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.openai.com/v1/fine_tuning/jobs?limit={limit}",
                headers=get_headers()
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"OpenAI API 오류: {response.text}"
                )
            
            return response.json()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파인튜닝 작업 목록 조회 오류: {str(e)}")

# 파인튜닝 작업 상태 조회
@router.get("/fine-tuning-jobs/{job_id}")
async def get_fine_tuning_job(job_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.openai.com/v1/fine_tuning/jobs/{job_id}",
                headers=get_headers()
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"OpenAI API 오류: {response.text}"
                )
            
            return response.json()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파인튜닝 작업 상태 조회 오류: {str(e)}")

# 유틸리티 함수들
async def monitor_fine_tuning_job(job_id: str):
    """백그라운드에서 파인튜닝 작업 상태를 모니터링합니다."""
    max_retries = 100
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.openai.com/v1/fine_tuning/jobs/{job_id}",
                    headers=get_headers()
                )
                
                if response.status_code == 200:
                    job_data = response.json()
                    status = job_data.get("status")
                    
                    # 작업이 완료되었거나 실패한 경우
                    if status in ["succeeded", "failed", "cancelled"]:
                        # 여기에 작업 완료 시 알림 로직 구현 (예: 데이터베이스 업데이트, 이메일 발송 등)
                        print(f"파인튜닝 작업 {job_id} 상태: {status}")
                        break
            
            # 대기 시간 (초기에는 짧게, 나중에는 길게)
            await asyncio.sleep(min(30, 5 + retry_count // 5))
            retry_count += 1
        
        except Exception as e:
            print(f"파인튜닝 작업 모니터링 오류: {str(e)}")
            await asyncio.sleep(60)  # 오류 발생 시 1분 대기
            retry_count += 1

def parse_qa_pairs(text: str, expected_pairs: int) -> List[Dict[str, Any]]:
    """
    생성된 텍스트에서 질문-답변 쌍을 파싱합니다.
    이 함수는 다양한 포맷을 처리할 수 있도록 구현해야 합니다.
    """
    pairs = []
    lines = text.split('\n')
    
    # 간단한 파싱 예시 (실제로는 더 강건한 파싱 필요)
    current_question = None
    current_answer = None
    
    for line in lines:
        line = line.strip()
        
        # 질문으로 시작하는 줄 감지
        if line.startswith("질문:") or line.startswith("Q:"):
            # 이전 Q&A 쌍이 있으면 저장
            if current_question and current_answer:
                pairs.append({
                    "messages": [
                        {"role": "user", "content": current_question},
                        {"role": "assistant", "content": current_answer}
                    ]
                })
            
            # 새 질문 시작
            current_question = line.split(":", 1)[1].strip()
            current_answer = None
        
        # 답변으로 시작하는 줄 감지
        elif (line.startswith("답변:") or line.startswith("A:")) and current_question:
            current_answer = line.split(":", 1)[1].strip()
        
        # 답변에 추가 내용이 있는 경우
        elif current_question and current_answer:
            current_answer += " " + line
    
    # 마지막 Q&A 쌍 추가
    if current_question and current_answer:
        pairs.append({
            "messages": [
                {"role": "user", "content": current_question},
                {"role": "assistant", "content": current_answer}
            ]
        })
    
    # 대안적인 파싱 방법: 번호가 매겨진 형식 (예: 1. 질문: ... 답변: ...)
    if not pairs:
        pattern_found = False
        
        for i, line in enumerate(lines):
            if not line.strip():
                continue
                
            # 번호로 시작하는 패턴 찾기
            if line.strip().startswith(('1.', '1)', '1:')):
                pattern_found = True
                break
        
        if pattern_found:
            current_item = None
            current_text = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 새 항목 시작 감지
                if any(line.startswith(f"{i}{sep}") for i in range(1, expected_pairs + 1) for sep in ['.', ')', ':']):
                    # 이전 항목 저장
                    if current_item and current_text:
                        parts = current_text.split('답변:', 1)
                        if len(parts) == 2:
                            q = parts[0].replace('질문:', '').strip()
                            a = parts[1].strip()
                            pairs.append({
                                "messages": [
                                    {"role": "user", "content": q},
                                    {"role": "assistant", "content": a}
                                ]
                            })
                    
                    # 새 항목 시작
                    current_item = line
                    current_text = line
                else:
                    # 현재 항목에 텍스트 추가
                    current_text += " " + line
            
            # 마지막 항목 저장
            if current_item and current_text:
                parts = current_text.split('답변:', 1)
                if len(parts) == 2:
                    q = parts[0].replace('질문:', '').strip()
                    for prefix in [f"{i}{sep}" for i in range(1, expected_pairs + 1) for sep in ['.', ')', ':']]:
                        if q.startswith(prefix):
                            q = q[len(prefix):].strip()
                            break
                    a = parts[1].strip()
                    pairs.append({
                        "messages": [
                            {"role": "user", "content": q},
                            {"role": "assistant", "content": a}
                        ]
                    })
    
    return pairs 