"""
SQLAlchemy 기본 클래스 정의
"""
from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    id: Any
    __name__: str
    
    # 테이블 이름 자동 생성
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() 