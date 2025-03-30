"""
노지AI재배관리시스템 실행 스크립트
"""
import argparse
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description="노지AI재배관리시스템")
    parser.add_argument("--prod", action="store_true", help="프로덕션 모드로 실행")
    args = parser.parse_args()
    
    # 설정
    host = settings.HOST
    port = settings.PORT
    reload = not args.prod
    
    # 항상 테스트 모드로 설정 (개발 편의성)
    reload = True
    
    # 시작 메시지
    mode = "테스트" if reload else "프로덕션"
    print(f"노지AI재배관리시스템을 {mode} 모드로 실행합니다.")
    print(f"서버 주소: http://{host}:{port}")
    
    # 서버 실행 - factory 패턴 사용
    uvicorn.run("app.main:create_app", 
                host=host, 
                port=port, 
                reload=reload, 
                factory=True) 