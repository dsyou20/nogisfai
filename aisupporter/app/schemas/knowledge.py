"""
경험지식 스키마 정의 모듈

API의 요청 및 응답 데이터 형식을 정의합니다.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 태그 스키마
class TagBase(BaseModel):
    name: str
    
class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class PopularTag(BaseModel):
    name: str
    count: int

# 카테고리 스키마
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# 지식 항목 스키마
class KnowledgeItemBase(BaseModel):
    question: str
    answer: str
    source: Optional[str] = None
    source_page: Optional[int] = None
    category_id: Optional[int] = None
    confidence: float = 1.0
    is_verified: bool = False

class KnowledgeItemCreate(KnowledgeItemBase):
    tags: Optional[List[str]] = None

class KnowledgeItemUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    source: Optional[str] = None
    source_page: Optional[int] = None
    category_id: Optional[int] = None
    confidence: Optional[float] = None
    is_verified: Optional[bool] = None
    tags: Optional[List[str]] = None

class KnowledgeItem(KnowledgeItemBase):
    id: int
    views: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[Category] = None
    tags: List[Tag] = []
    
    class Config:
        orm_mode = True

# 지식 항목 목록 응답
class KnowledgeItemList(BaseModel):
    items: List[KnowledgeItem]
    total: int
    skip: int
    limit: int

# 검색 관련 스키마
class KnowledgeSearchQuery(BaseModel):
    query: str
    limit: Optional[int] = 5
    threshold: Optional[float] = 0.7

# 배치 생성 스키마
class KnowledgeBatchCreate(BaseModel):
    items: List[KnowledgeItemCreate] 