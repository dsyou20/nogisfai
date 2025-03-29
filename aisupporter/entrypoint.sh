#!/bin/bash
set -e

# 필수 디렉토리 존재 확인 및 없는 경우에만 생성
echo "필수 디렉토리 확인 중..."
if [ ! -d "/home/jovyan/data" ]; then
    echo "데이터 디렉토리가 없어 새로 생성합니다."
    mkdir -p /home/jovyan/data
else
    echo "기존 데이터 디렉토리를 유지합니다."
fi

if [ ! -d "/home/jovyan/data/parquet" ]; then
    echo "parquet 디렉토리가 없어 새로 생성합니다."
    mkdir -p /home/jovyan/data/parquet
else
    echo "기존 parquet 디렉토리를 유지합니다."
fi

# 모든 볼륨 디렉토리에 대한 권한 설정
echo "볼륨 디렉토리 권한 설정 중..."
chmod -R 777 /home/jovyan/data
chmod -R 777 /home/jovyan/bizlogic
[ -d "/app/data" ] && chmod -R 777 /app/data

# 기존 파일에 대한 권한도 확인 (너무 많은 파일이 있는 경우 시간이 오래 걸릴 수 있음)
echo "파일 권한 설정 중..."
find /home/jovyan/data -type f -exec chmod 666 {} \; 2>/dev/null || true
find /home/jovyan/bizlogic -type f -exec chmod 666 {} \; 2>/dev/null || true
[ -d "/app/data" ] && find /app/data -type f -exec chmod 666 {} \; 2>/dev/null || true

# 사용자 jovyan에게 디렉토리 소유권 부여
echo "소유권 설정 중..."
chown -R jovyan:users /home/jovyan/data || true
chown -R jovyan:users /home/jovyan/bizlogic || true
[ -d "/app/data" ] && chown -R jovyan:users /app/data || true

echo "볼륨 디렉토리 권한 설정 완료"
echo "root 사용자로 애플리케이션 시작..."

# 실행 경로 확인
if [ ! -f "/home/jovyan/bizlogic/main.py" ]; then
    echo "오류: main.py 파일을 찾을 수 없습니다!"
    ls -la /home/jovyan/bizlogic
    exit 1
fi

# 환경 변수 설정
export PYTHONPATH=/home/jovyan/bizlogic:$PYTHONPATH

# 로그 디렉토리 생성
mkdir -p /home/jovyan/logs
chmod 777 /home/jovyan/logs

# 로그 파일 경로 설정
LOG_FILE="/home/jovyan/logs/app.log"

# FastAPI 애플리케이션 실행 (uvicorn 사용)
cd /home/jovyan/bizlogic && python -m uvicorn main:app --host 0.0.0.0 --port 8080 --log-level info > $LOG_FILE 2>&1 || {
    echo "애플리케이션 실행 중 오류가 발생했습니다. 로그 확인: $LOG_FILE"
    cat $LOG_FILE
    exit 1
} 