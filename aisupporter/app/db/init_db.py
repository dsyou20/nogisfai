"""
데이터베이스 초기화 모듈

이 모듈은 데이터베이스를 초기화하고 기본 데이터를 생성하는 기능을 제공합니다.
"""
import os
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database

from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.repositories.knowledge_repository import KnowledgeRepository
from app.core.config import settings

logger = logging.getLogger(__name__)

def init_db() -> None:
    """
    데이터베이스 테이블을 생성하고 기본 데이터를 넣습니다.
    애플리케이션 시작 시 실행됩니다.
    """
    # SQLite 데이터베이스 파일 경로 확인 (sqlite:///./app.db 형식인 경우)
    if settings.DATABASE_URL.startswith('sqlite:///'):
        db_path = settings.DATABASE_URL.replace('sqlite:///', '')
        # 상대 경로인 경우 절대 경로로 변환
        if db_path.startswith('./'):
            db_path = os.path.join(os.getcwd(), db_path[2:])
        
        # 데이터베이스 파일이 있는 디렉토리 생성
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    
    # 다른 종류의 데이터베이스인 경우, 데이터베이스가 없으면 생성
    if not database_exists(engine.url):
        logger.info(f"데이터베이스 생성: {settings.DATABASE_URL}")
        create_database(engine.url)
    
    # 테이블이 없으면 생성
    Base.metadata.create_all(bind=engine)
    logger.info("데이터베이스 테이블 생성 완료")
    
    # 초기 데이터 생성
    db = SessionLocal()
    try:
        # 기본 카테고리 생성
        create_initial_categories(db)
    finally:
        db.close()

def create_initial_categories(db: Session) -> None:
    """
    기본 카테고리 생성
    """
    # 기존 카테고리가 있는지 확인
    categories = KnowledgeRepository.get_categories(db)
    if categories:
        logger.info("카테고리가 이미 존재합니다. 건너뜁니다.")
        return
    
    # 기본 카테고리 생성
    categories = [
        {"name": "질병 관리", "description": "작물 질병 관련 지식"},
        {"name": "해충 관리", "description": "작물 해충 관련 지식"},
        {"name": "영양 관리", "description": "작물 영양 관련 지식"},
        {"name": "수분 관리", "description": "작물 수분 관련 지식"},
        {"name": "재배 기술", "description": "작물 재배 기술 관련 지식"},
        {"name": "수확 관리", "description": "작물 수확 관련 지식"},
        {"name": "기상 정보", "description": "기상 정보 관련 지식"},
        {"name": "장비 관리", "description": "농업 장비 관련 지식"},
        {"name": "농약 사용", "description": "농약 사용 관련 지식"},
        {"name": "일반 지식", "description": "기타 일반 농업 지식"},
    ]
    
    for category in categories:
        KnowledgeRepository.create_category(
            db=db,
            name=category["name"],
            description=category["description"]
        )
    
    logger.info(f"{len(categories)}개의 기본 카테고리가 생성되었습니다.") 