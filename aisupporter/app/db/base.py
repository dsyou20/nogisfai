"""
이 파일은 모든 데이터베이스 모델을 가져와서 Alembic이 마이그레이션을 생성할 때 사용할 수 있도록 합니다.
"""

from app.db.base_class import Base
from app.models.knowledge import KnowledgeCategory, KnowledgeItem, KnowledgeTag, KnowledgeItemTag 