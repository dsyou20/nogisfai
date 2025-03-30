"""
경험지식 데이터베이스 저장소 모듈

경험지식을 데이터베이스에 저장하고 관리하는 기능을 제공합니다.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from app.models.knowledge import KnowledgeItem, KnowledgeCategory, KnowledgeTag, KnowledgeItemTag

class KnowledgeRepository:
    """경험지식 저장소 클래스"""
    
    @staticmethod
    def create_knowledge_item(
        db: Session,
        question: str,
        answer: str,
        source: Optional[str] = None,
        source_page: Optional[int] = None,
        category_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        confidence: float = 1.0,
    ) -> KnowledgeItem:
        """
        새로운 지식 항목을 생성합니다.
        
        Args:
            db: 데이터베이스 세션
            question: 질문 내용
            answer: 답변 내용
            source: 출처 (선택적)
            source_page: 출처 페이지 번호 (선택적)
            category_id: 카테고리 ID (선택적)
            tags: 태그 목록 (선택적)
            confidence: 신뢰도 점수 (기본값: 1.0)
            
        Returns:
            생성된 지식 항목
        """
        # 새 지식 항목 생성
        db_item = KnowledgeItem(
            question=question,
            answer=answer,
            source=source,
            source_page=source_page,
            category_id=category_id,
            confidence=confidence
        )
        
        db.add(db_item)
        db.flush()  # ID를 얻기 위해 flush
        
        # 태그 처리
        if tags:
            for tag_name in tags:
                # 태그가 존재하는지 확인하고 없으면 생성
                db_tag = db.query(KnowledgeTag).filter(KnowledgeTag.name == tag_name).first()
                if not db_tag:
                    db_tag = KnowledgeTag(name=tag_name)
                    db.add(db_tag)
                    db.flush()
                
                # 지식 항목과 태그 연결
                db_item_tag = KnowledgeItemTag(
                    knowledge_item_id=db_item.id,
                    tag_id=db_tag.id
                )
                db.add(db_item_tag)
        
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    def get_knowledge_item(db: Session, item_id: int) -> Optional[KnowledgeItem]:
        """
        ID로 지식 항목을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            item_id: 지식 항목 ID
            
        Returns:
            지식 항목 또는 None
        """
        return db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    
    @staticmethod
    def get_knowledge_items(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        tag: Optional[str] = None,
        search_query: Optional[str] = None,
        verified_only: bool = False
    ) -> List[KnowledgeItem]:
        """
        지식 항목 목록을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 항목 수
            limit: 최대 항목 수
            category_id: 카테고리 ID 필터 (선택적)
            tag: 태그 필터 (선택적)
            search_query: 검색어 (선택적)
            verified_only: 검증된 항목만 조회 여부
            
        Returns:
            지식 항목 목록
        """
        query = db.query(KnowledgeItem)
        
        # 필터 적용
        if category_id:
            query = query.filter(KnowledgeItem.category_id == category_id)
        
        if verified_only:
            query = query.filter(KnowledgeItem.is_verified == True)
        
        if search_query:
            search = f"%{search_query}%"
            query = query.filter(
                or_(
                    KnowledgeItem.question.ilike(search),
                    KnowledgeItem.answer.ilike(search)
                )
            )
        
        if tag:
            query = query.join(KnowledgeItemTag).join(KnowledgeTag).filter(KnowledgeTag.name == tag)
        
        # 정렬 및 페이징
        return query.order_by(desc(KnowledgeItem.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_knowledge_item(
        db: Session,
        item_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[KnowledgeItem]:
        """
        지식 항목을 업데이트합니다.
        
        Args:
            db: 데이터베이스 세션
            item_id: 지식 항목 ID
            update_data: 업데이트할 데이터
            
        Returns:
            업데이트된 지식 항목 또는 None
        """
        db_item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
        if not db_item:
            return None
        
        # 태그 처리
        tags = update_data.pop("tags", None)
        
        # 다른 필드 업데이트
        for key, value in update_data.items():
            if hasattr(db_item, key):
                setattr(db_item, key, value)
        
        # 태그 업데이트
        if tags is not None:
            # 기존 태그 관계 삭제
            db.query(KnowledgeItemTag).filter(
                KnowledgeItemTag.knowledge_item_id == item_id
            ).delete()
            
            # 새 태그 추가
            for tag_name in tags:
                db_tag = db.query(KnowledgeTag).filter(KnowledgeTag.name == tag_name).first()
                if not db_tag:
                    db_tag = KnowledgeTag(name=tag_name)
                    db.add(db_tag)
                    db.flush()
                
                db_item_tag = KnowledgeItemTag(
                    knowledge_item_id=item_id,
                    tag_id=db_tag.id
                )
                db.add(db_item_tag)
        
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    def delete_knowledge_item(db: Session, item_id: int) -> bool:
        """
        지식 항목을 삭제합니다.
        
        Args:
            db: 데이터베이스 세션
            item_id: 지식 항목 ID
            
        Returns:
            성공 여부
        """
        db_item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
        if not db_item:
            return False
        
        # 태그 관계 삭제
        db.query(KnowledgeItemTag).filter(
            KnowledgeItemTag.knowledge_item_id == item_id
        ).delete()
        
        # 항목 삭제
        db.delete(db_item)
        db.commit()
        return True
    
    @staticmethod
    def search_similar_questions(
        db: Session,
        query: str,
        limit: int = 5,
        threshold: float = 0.7  # 유사도 임계값
    ) -> List[KnowledgeItem]:
        """
        유사한 질문을 검색합니다.
        
        참고: 실제 구현에서는 벡터 DB나 임베딩 검색 로직을 추가해야 합니다.
        현재는 간단한 키워드 검색으로 대체합니다.
        
        Args:
            db: 데이터베이스 세션
            query: 검색어
            limit: 최대 결과 수
            threshold: 유사도 임계값
            
        Returns:
            유사한 질문 목록
        """
        search = f"%{query}%"
        return db.query(KnowledgeItem).filter(
            KnowledgeItem.question.ilike(search)
        ).order_by(desc(KnowledgeItem.views)).limit(limit).all()
    
    @staticmethod
    def increment_view_count(db: Session, item_id: int) -> bool:
        """
        지식 항목의 조회수를 증가시킵니다.
        
        Args:
            db: 데이터베이스 세션
            item_id: 지식 항목 ID
            
        Returns:
            성공 여부
        """
        db_item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
        if not db_item:
            return False
        
        db_item.views += 1
        db.commit()
        return True
    
    # 카테고리 관련 메서드
    @staticmethod
    def create_category(db: Session, name: str, description: Optional[str] = None) -> KnowledgeCategory:
        """
        새로운 카테고리를 생성합니다.
        
        Args:
            db: 데이터베이스 세션
            name: 카테고리 이름
            description: 카테고리 설명 (선택적)
            
        Returns:
            생성된 카테고리
        """
        db_category = KnowledgeCategory(name=name, description=description)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[KnowledgeCategory]:
        """
        카테고리 목록을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 항목 수
            limit: 최대 항목 수
            
        Returns:
            카테고리 목록
        """
        return db.query(KnowledgeCategory).offset(skip).limit(limit).all()
    
    # 태그 관련 메서드
    @staticmethod
    def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[KnowledgeTag]:
        """
        태그 목록을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 항목 수
            limit: 최대 항목 수
            
        Returns:
            태그 목록
        """
        return db.query(KnowledgeTag).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_popular_tags(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        인기 태그 목록을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            limit: 최대 항목 수
            
        Returns:
            [{'name': 태그명, 'count': 사용 횟수}] 형태의 태그 목록
        """
        tag_counts = db.query(
            KnowledgeTag.name.label('name'),
            func.count(KnowledgeItemTag.tag_id).label('count')
        ).join(
            KnowledgeItemTag, KnowledgeTag.id == KnowledgeItemTag.tag_id
        ).group_by(
            KnowledgeTag.name
        ).order_by(
            desc('count')
        ).limit(limit).all()
        
        return [{'name': name, 'count': count} for name, count in tag_counts] 