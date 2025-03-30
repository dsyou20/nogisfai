import os
from datetime import timedelta

# 기본 디렉토리 설정
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 보안 설정
SECRET_KEY = 'dev-secret-key-change-in-production'  # 실제 운영 환경에서는 변경 필요
SESSION_COOKIE_SECURE = False  # HTTPS를 사용하는 경우 True로 설정
REMEMBER_COOKIE_DURATION = timedelta(days=14)  # 로그인 유지 기간

# 애플리케이션 설정
DEBUG = True  # 개발 모드 활성화, 운영 환경에서는 False로 변경
TESTING = False
CSRF_ENABLED = True
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'csrf-secret-key-change-in-production'  # 실제 운영 환경에서는 변경 필요

# 데이터베이스 설정
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')  # SQLite 사용, 필요시 다른 DB로 변경
SQLALCHEMY_TRACK_MODIFICATIONS = False  # 성능 향상을 위해 비활성화
SQLALCHEMY_ECHO = False  # SQL 디버깅을 위해 True로 설정하면 쿼리가 로그에 출력됨

# 파일 업로드 설정
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 최대 16MB 파일 업로드 허용
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')

# 로깅 설정
LOG_LEVEL = 'INFO'  # 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' 중 선택

# API 관련 설정
API_RATE_LIMIT = '100/hour'  # API 호출 제한

# DuckDB 설정
DUCKDB_DATA_PATH = os.path.join(BASE_DIR, 'app', 'data', 'parquet') 