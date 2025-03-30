"""
경험지식 데이터베이스 모델 정의
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from typing import List, Optional
from datetime import datetime

class KnowledgeCategory(Base):
    """지식 카테고리 모델"""
    __tablename__ = "knowledge_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 정의
    knowledge_items = relationship("KnowledgeItem", back_populates="category")
    
    def __repr__(self):
        return f"<KnowledgeCategory {self.name}>"

class KnowledgeItem(Base):
    """지식 항목 모델"""
    __tablename__ = "knowledge_items"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)  # 지식 출처
    source_page = Column(Integer, nullable=True)  # 출처 페이지 번호
    confidence = Column(Float, default=1.0)  # 신뢰도 점수
    is_verified = Column(Boolean, default=False)  # 검증 여부
    views = Column(Integer, default=0)  # 조회수
    category_id = Column(Integer, ForeignKey("knowledge_categories.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 정의
    category = relationship("KnowledgeCategory", back_populates="knowledge_items")
    tags = relationship("KnowledgeTag", secondary="knowledge_item_tags", back_populates="knowledge_items")
    
    def __repr__(self):
        return f"<KnowledgeItem {self.question[:30]}...>"

class KnowledgeTag(Base):
    """지식 태그 모델"""
    __tablename__ = "knowledge_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 정의
    knowledge_items = relationship("KnowledgeItem", secondary="knowledge_item_tags", back_populates="tags")
    
    def __repr__(self):
        return f"<KnowledgeTag {self.name}>"

class KnowledgeItemTag(Base):
    """지식 항목과 태그 간의 다대다 관계 테이블"""
    __tablename__ = "knowledge_item_tags"
    
    knowledge_item_id = Column(Integer, ForeignKey("knowledge_items.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("knowledge_tags.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 