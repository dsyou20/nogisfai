"""
데이터베이스 초기화 스크립트

이 스크립트는 데이터베이스를 초기화하고 기본 데이터를 생성합니다.
데이터베이스가 존재하지 않을 경우 자동으로 생성합니다.
"""
import os
import sys
import logging
from pathlib import Path
from sqlalchemy_utils import database_exists, create_database

# 프로젝트 루트 경로를 파이썬 경로에 추가
# 이렇게 하면 app 패키지를 임포트할 수 있습니다.
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from sqlalchemy.orm import Session
from app.db.session import engine
from app.db.base import Base
from app.repositories.knowledge_repository import KnowledgeRepository
from app.db.session import SessionLocal
from app.core.config import settings

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    """
    데이터베이스를 초기화합니다.
    
    1. 데이터베이스가 존재하지 않으면 생성합니다.
    2. 테이블을 생성합니다.
    3. 기본 데이터를 넣습니다.
    """
    # 데이터베이스 URL 확인
    db_url = settings.DATABASE_URL
    logger.info(f"데이터베이스 URL: {db_url}")
    
    # 데이터베이스가 존재하지 않으면 생성
    if not database_exists(db_url):
        logger.info("데이터베이스가 존재하지 않습니다. 새로 생성합니다...")
        create_database(db_url)
        logger.info("데이터베이스가 생성되었습니다.")
    else:
        logger.info("데이터베이스가 이미 존재합니다.")
    
    # 데이터베이스 테이블 생성
    logger.info("테이블을 생성합니다...")
    Base.metadata.create_all(bind=engine)
    logger.info("테이블 생성이 완료되었습니다.")
    
    # 초기 데이터 생성
    db = SessionLocal()
    try:
        # 기본 카테고리 생성
        create_initial_categories(db)
        
        logger.info("데이터베이스 초기화 완료!")
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

if __name__ == "__main__":
    logger.info("데이터베이스 초기화 중...")
    init_db()
    logger.info("완료!") 