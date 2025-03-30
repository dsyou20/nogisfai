"""
경험지식 API 모듈

경험지식 추가, 삭제, 조회 등의 API 엔드포인트를 제공합니다.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from app.schemas.knowledge import (
    KnowledgeItemCreate, KnowledgeItem, 
    KnowledgeItemList, KnowledgeItemUpdate
)
from app.repositories.knowledge_repository import KnowledgeRepository
from app.db.session import get_db

# 라우터 정의
router = APIRouter()

# 경험지식 목록 조회
@router.get("/experience-knowledge", response_model=KnowledgeItemList)
async def get_experience_knowledge(
    skip: int = Query(0, description="건너뛸 항목 수"),
    limit: int = Query(10, description="조회할 항목 수"),
    category_id: Optional[int] = Query(None, description="카테고리 ID로 필터링"),
    tag: Optional[str] = Query(None, description="태그로 필터링"),
    search: Optional[str] = Query(None, description="검색어"),
    verified_only: bool = Query(False, description="검증된 항목만 조회"),
    db: Session = Depends(get_db)
):
    """
    경험지식 목록을 조회합니다.
    
    - **skip**: 건너뛸 항목 수
    - **limit**: 조회할 항목 수
    - **category_id**: 카테고리 ID로 필터링 (선택적)
    - **tag**: 태그로 필터링 (선택적)
    - **search**: 검색어 (선택적)
    - **verified_only**: 검증된 항목만 조회 여부
    """
    items = KnowledgeRepository.get_knowledge_items(
        db=db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        tag=tag,
        search_query=search,
        verified_only=verified_only
    )
    
    # 전체 항목 수 계산을 위한 쿼리 수행
    total_count = len(KnowledgeRepository.get_knowledge_items(
        db=db, 
        category_id=category_id,
        tag=tag,
        search_query=search,
        verified_only=verified_only
    ))
    
    return {
        "items": items,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }

# 경험지식 단일 항목 조회
@router.get("/experience-knowledge/{item_id}", response_model=KnowledgeItem)
async def get_experience_knowledge_item(
    item_id: int = Path(..., description="조회할 지식 항목 ID"),
    db: Session = Depends(get_db)
):
    """
    ID로 경험지식 항목을 조회합니다.
    
    - **item_id**: 조회할 지식 항목 ID
    """
    item = KnowledgeRepository.get_knowledge_item(db=db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="지식 항목을 찾을 수 없습니다")
    
    # 조회수 증가
    KnowledgeRepository.increment_view_count(db=db, item_id=item_id)
    
    return item

# 경험지식 추가
@router.post("/experience-knowledge", response_model=KnowledgeItem)
async def create_experience_knowledge(
    item: KnowledgeItemCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 경험지식 항목을 생성합니다.
    
    - **item**: 생성할 지식 항목 정보
    """
    return KnowledgeRepository.create_knowledge_item(
        db=db,
        question=item.question,
        answer=item.answer,
        source=item.source,
        source_page=item.source_page,
        category_id=item.category_id,
        tags=item.tags,
        confidence=item.confidence
    )

# 경험지식 수정
@router.put("/experience-knowledge/{item_id}", response_model=KnowledgeItem)
async def update_experience_knowledge(
    item_id: int,
    item_update: KnowledgeItemUpdate,
    db: Session = Depends(get_db)
):
    """
    기존 경험지식 항목을 수정합니다.
    
    - **item_id**: 수정할 지식 항목 ID
    - **item_update**: 수정할 내용
    """
    # 항목 존재 여부 확인
    existing_item = KnowledgeRepository.get_knowledge_item(db=db, item_id=item_id)
    if not existing_item:
        raise HTTPException(status_code=404, detail="지식 항목을 찾을 수 없습니다")
    
    # 업데이트 데이터 준비
    update_data = item_update.dict(exclude_unset=True)
    
    # 항목 수정
    updated_item = KnowledgeRepository.update_knowledge_item(
        db=db,
        item_id=item_id,
        update_data=update_data
    )
    
    return updated_item

# 경험지식 삭제
@router.delete("/experience-knowledge/{item_id}", response_model=dict)
async def delete_experience_knowledge(
    item_id: int = Path(..., description="삭제할 지식 항목 ID"),
    db: Session = Depends(get_db)
):
    """
    경험지식 항목을 삭제합니다.
    
    - **item_id**: 삭제할 지식 항목 ID
    """
    # 항목 존재 여부 확인
    existing_item = KnowledgeRepository.get_knowledge_item(db=db, item_id=item_id)
    if not existing_item:
        raise HTTPException(status_code=404, detail="지식 항목을 찾을 수 없습니다")
    
    # 항목 삭제
    success = KnowledgeRepository.delete_knowledge_item(db=db, item_id=item_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="지식 항목 삭제 중 오류가 발생했습니다")
    
    return {"success": True, "message": "지식 항목이 삭제되었습니다"}

# 카테고리 목록 조회
@router.get("/experience-knowledge/categories/list", response_model=List)
async def get_categories(
    skip: int = Query(0, description="건너뛸 항목 수"),
    limit: int = Query(100, description="조회할 항목 수"),
    db: Session = Depends(get_db)
):
    """
    지식 카테고리 목록을 조회합니다.
    
    - **skip**: 건너뛸 항목 수
    - **limit**: 조회할 항목 수
    """
    return KnowledgeRepository.get_categories(db=db, skip=skip, limit=limit)

# 태그 목록 조회
@router.get("/experience-knowledge/tags/list", response_model=List)
async def get_tags(
    skip: int = Query(0, description="건너뛸 항목 수"),
    limit: int = Query(100, description="조회할 항목 수"),
    db: Session = Depends(get_db)
):
    """
    지식 태그 목록을 조회합니다.
    
    - **skip**: 건너뛸 항목 수
    - **limit**: 조회할 항목 수
    """
    return KnowledgeRepository.get_tags(db=db, skip=skip, limit=limit)

# 인기 태그 목록 조회
@router.get("/experience-knowledge/tags/popular", response_model=List)
async def get_popular_tags(
    limit: int = Query(10, description="조회할 항목 수"),
    db: Session = Depends(get_db)
):
    """
    인기 태그 목록을 조회합니다.
    
    - **limit**: 조회할 항목 수
    """
    return KnowledgeRepository.get_popular_tags(db=db, limit=limit) 