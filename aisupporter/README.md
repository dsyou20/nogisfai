# 스마트 콩 재배 AI 자동제어 시스템

콩 재배를 위한 인공지능 기반 자동 제어 시스템으로, 센서 데이터와 영상 분석을 통해 최적의 생육 조건을 유지하고 병해충을 조기에 발견하여 생산성과 품질을 향상시키는 스마트팜 솔루션입니다.

## 🌱 주요 기능

- **센서 데이터 실시간 모니터링**: 온도, 습도, 토양 수분, 광량 등 환경 데이터 수집/분석
- **AI 기반 자동 제어**: 최적 생육 조건을 유지하기 위한 관수, 비료, 온도 등 자동 제어
- **작물 상태 영상 분석**: 영상 기반 생육 상태 및 병해충 감지
- **수확량 예측**: 축적된 데이터 기반 수확량 예측 및 최적 수확 시점 결정
- **ESG 지표 분석**: 물 사용량, 에너지 사용, 탄소 발자국 등 환경 지표 관리
- **AI 챗봇 어시스턴트**: 작물 관리에 대한 질문 응답 및 조언 제공

## 🔧 시스템 요구사항

- Python 3.10 이상
- FastAPI, DuckDB, LangChain, LangGraph
- 현대적인 웹 브라우저 (Chrome, Firefox, Edge, Safari 최신 버전)

## 📦 설치 방법

1. 저장소 클론
    ```bash
    git clone https://github.com/dsyou20/nogisfai.git
    cd nogisfai
    ```

2. Conda 환경 생성 및 활성화
    ```bash
    conda create -n nogi python=3.10
    conda activate nogi
    ```

3. 필요 패키지 설치
    ```bash
    pip install -r requirements.txt
    ```

## 🐳 도커 컴포즈 실행 방법

1. 도커와 도커 컴포즈가 설치되어 있는지 확인
    ```bash
    docker --version
    docker-compose --version
    ```

2. 개발 환경용 도커 컴포즈 파일(docker-compose-nogiai-dev.yml)로 서비스 빌드 및 실행
    ```bash
    docker-compose -f docker-compose-nogiai-dev.yml build
    docker-compose -f docker-compose-nogiai-dev.yml up -d
    ```

3. 서비스 상태 확인
    ```bash
    docker-compose -f docker-compose-nogiai-dev.yml ps
    ```

4. 로그 확인
    ```bash
    docker-compose -f docker-compose-nogiai-dev.yml logs
    ```

5. 실시간 로그 확인
    ```bash
    docker-compose -f docker-compose-nogiai-dev.yml logs -f
    ```

6. 서비스 중지 및 삭제
    ```bash
    docker-compose -f docker-compose-nogiai-dev.yml down
    ```



도커 컴포즈 개발 환경으로 실행 시 다음 주소에서 서비스에 접근할 수 있습니다:
- 홈페이지: http://localhost:8000
- 대시보드: http://localhost:8000/dashboard
- API 문서: http://localhost:8000/docs

## 🚀 실행 방법

1. 개발 모드로 실행
    ```bash
    conda activate nogi
    python app.py
    ```

2. 프로덕션 모드로 실행
    ```bash
    conda activate nogi
    python app.py --prod
    ```

3. 웹 브라우저에서 다음 주소로 접속
    - 홈페이지: http://localhost:8000
    - 대시보드: http://localhost:8000/dashboard

## 📊 대시보드 기능

- **환경 모니터링**: 온도, 습도, 토양 수분, 광량 등 실시간 환경 데이터 차트
- **AI 제어 상태**: 현재 AI 제어 상태 및 최근 제어 이력
- **작물 상태**: 생육 단계, 건강 상태, 예상 수확량 등
- **알림 및 경고**: 이상치 감지 및 조치 필요 사항 알림
- **ESG 지표**: 물, 에너지 사용량 및 환경 영향 지표

## 📚 API 문서

API 문서는 서버 실행 후 다음 주소에서 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧩 시스템 구조

```
[센서·영상·이력 데이터] ──────→ [데이터 수집/처리 모듈]
          ↑                              ↓
[제어 명령 실행] ← [AI 제어 모듈] ← [상태 분석 모듈]
                        ↓
                [대시보드 UI / API]
```

## 📁 디렉토리 구조

```
smart-soybean-ai/
├── app/                  # 메인 애플리케이션 코드
│   ├── api/              # API 라우터
│   ├── core/             # 핵심 설정 및 유틸리티
│   ├── db/               # 데이터베이스 모듈
│   ├── llm/              # LLM 관련 코드
│   ├── models/           # 데이터 모델
│   └── templates/        # HTML 템플릿
├── static/               # 정적 파일
│   ├── css/              # 스타일시트
│   ├── js/               # 자바스크립트
│   └── images/           # 이미지
├── app.py                # 메인 애플리케이션 엔트리 포인트
├── requirements.txt      # 필요 패키지 목록
└── README.md             # 사용 설명서
```

## 📝 사용 예시

1. 대시보드에서 실시간 환경 데이터 모니터링
2. AI 기반 자동 제어 설정 및 조정
3. 작물 상태 확인 및 이상 징후 알림 확인
4. ESG 지표 분석 및 개선점 확인
5. 챗봇을 통한 작물 관리 질문 및 조언 받기

## 🤝 기여 방법

1. Fork 저장소를 생성합니다.
2. Feature 브랜치를 생성합니다: `git checkout -b feature/my-feature`
3. 변경사항을 커밋합니다: `git commit -m 'Add some feature'`
4. 브랜치에 Push합니다: `git push origin feature/my-feature`
5. Pull Request를 제출합니다.

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 연락처

- 이메일: support@smartsoybean.ai
- 웹사이트: https://smartsoybean.ai
