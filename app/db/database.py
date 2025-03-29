"""
DuckDB 데이터베이스 연결 및 관리 모듈
"""
import os
import duckdb
from pathlib import Path

from app.core.config import settings

class Database:
    """DuckDB 데이터베이스 관리 클래스"""
    
    def __init__(self, db_path=None):
        """
        데이터베이스 연결 초기화
        
        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path or settings.DB_PATH
        self._ensure_db_directory()
        self.conn = None
    
    def _ensure_db_directory(self):
        """데이터베이스 디렉토리가 존재하는지 확인하고 없으면 생성"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def connect(self):
        """데이터베이스 연결"""
        if self.conn is None:
            self.conn = duckdb.connect(self.db_path)
        return self.conn
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.conn is not None:
            self.conn.close()
            self.conn = None
    
    def execute(self, query, params=None):
        """
        SQL 쿼리 실행
        
        Args:
            query: 실행할 SQL 쿼리
            params: 쿼리 파라미터
            
        Returns:
            쿼리 실행 결과
        """
        conn = self.connect()
        try:
            if params:
                return conn.execute(query, params)
            return conn.execute(query)
        except Exception as e:
            print(f"쿼리 실행 중 오류 발생: {e}")
            raise
    
    def query_df(self, query, params=None):
        """
        SQL 쿼리 실행하고 Pandas DataFrame으로 반환
        
        Args:
            query: 실행할 SQL 쿼리
            params: 쿼리 파라미터
            
        Returns:
            DataFrame 형태의 쿼리 결과
        """
        conn = self.connect()
        try:
            if params:
                return conn.execute(query, params).fetchdf()
            return conn.execute(query).fetchdf()
        except Exception as e:
            print(f"DataFrame 쿼리 실행 중 오류 발생: {e}")
            raise
    
    def load_parquet(self, table_name, parquet_path):
        """
        Parquet 파일을 테이블로 로드
        
        Args:
            table_name: 생성할 테이블 이름
            parquet_path: Parquet 파일 경로
            
        Returns:
            로드된 행 수
        """
        query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} AS 
            SELECT * FROM read_parquet('{parquet_path}')
        """
        self.execute(query)
        count_query = f"SELECT COUNT(*) FROM {table_name}"
        result = self.execute(count_query).fetchone()
        return result[0] if result else 0
    
    def parquet_to_db(self, base_dir=None):
        """
        디렉토리 내의 모든 Parquet 파일을 데이터베이스에 로드
        
        Args:
            base_dir: Parquet 파일이 있는 디렉토리
            
        Returns:
            로드된 파일 수
        """
        base_dir = base_dir or settings.PARQUET_DIR
        if not os.path.exists(base_dir):
            print(f"Parquet 디렉토리가 존재하지 않습니다: {base_dir}")
            return 0
            
        loaded_files = 0
        for file_path in Path(base_dir).glob("**/*.parquet"):
            rel_path = os.path.relpath(file_path, base_dir)
            table_name = rel_path.replace("/", "_").replace(".", "_")
            rows = self.load_parquet(table_name, str(file_path))
            print(f"테이블 '{table_name}'에 {rows}개 행 로드됨")
            loaded_files += 1
        
        return loaded_files

# 전역 데이터베이스 인스턴스
db = Database() 