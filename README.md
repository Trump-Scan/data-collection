# 데이터 수집 레이어 (Data Collection Layer)

트럼프 스캔 서비스의 데이터 수집 레이어입니다. 여러 채널에서 트럼프 대통령의 발언을 실시간으로 모니터링하고 수집합니다.

---

## 📋 프로젝트 개요

### 목적
다양한 소셜 미디어, 뉴스 매체, 공식 발표 채널에서 트럼프 대통령의 발언을 자동으로 수집하여 다음 레이어(분석 레이어)로 전달합니다.

### 핵심 책임
- 여러 채널 동시 모니터링 (Truth Social, 뉴스 등)
- 실시간/준실시간 수집 (5-10분 간격)
- 중복 수집 방지 (Checkpoint 관리)
- 원본 데이터 저장 및 구조화
- 다음 레이어로 메시지 발행

### 채널별 수집 방법

| 채널 | 수집 방식 | 엔드포인트/대상 | 수집 주기 | 구현 상태 |
|------|-----------|----------------|-----------|-----------|
| **Truth Social** | RSS 피드 API 호출 | `https://trumpstruth.org/feed` | 5분 | ✅ 구현 완료 |
| **뉴스** | 웹 크롤링 | 주요 뉴스 사이트 | 10분 | 📋 계획됨 |

**수집 방식 설명:**
- **RSS 피드**: feedparser를 사용한 표준 RSS 파싱
- **웹 크롤링**: httpx + BeautifulSoup를 사용한 HTML 파싱

### 처리 흐름
```
Orchestrator
  ↓
각 Collector에 대해:
  1. Checkpoint 조회 (StateStore)
  2. collect_raw_data(checkpoint) 호출
  3. 원본 저장 (Database)
  4. 메시지 발행 (MessageQueue)
  5. Checkpoint 저장 (StateStore)
```

---

## 🏗️ 패키지 구조

```
data-collection/
├── src/
│   ├── collectors/              # 채널별 Collector
│   │   ├── __init__.py
│   │   ├── base.py             # BaseCollector 추상 클래스
│   │   ├── truth_social.py     # Truth Social Collector (구현 완료)
│   │   └── dummy.py            # Dummy Collector (테스트용)
│   │
│   ├── infrastructure/          # 인프라 레이어
│   │   ├── __init__.py
│   │   ├── message_queue.py    # Redis Streams 클라이언트
│   │   ├── state_store.py      # Redis Checkpoint 관리
│   │   └── database.py         # Oracle DB 연결
│   │
│   ├── models/                  # 데이터 모델
│   │   ├── __init__.py
│   │   ├── channel.py          # Channel Enum 정의
│   │   └── raw_data.py         # RawData Pydantic 모델
│   │
│   ├── orchestrator.py         # Collector 조율 및 스케줄링
│   └── logger.py               # 구조화된 로깅 설정
│
├── config/                      # 설정 파일
│   ├── __init__.py
│   ├── database.py             # DB 설정 (gitignore)
│   ├── database.example.py     # DB 설정 템플릿
│   ├── redis.py                # Redis 설정 (gitignore)
│   ├── redis.example.py        # Redis 설정 템플릿
│   └── scheduler.py            # 스케줄러 설정
│
├── sql/                         # 데이터베이스 스키마
│   └── ddl.sql                 # 테이블 생성 SQL
│
├── tests/                       # 테스트
│   ├── __init__.py
│   └── test_truth_social_collector.py
│
├── claudedocs/                  # 개발 문서
│   └── develop_step.md         # 단계별 개발 가이드
│
├── requirements.txt
└── main.py                     # 진입점
```

### 주요 컴포넌트 설명

#### `collectors/`
- **`base.py`**: BaseCollector 추상 클래스
  - 모든 Collector가 구현해야 할 인터페이스 정의
  - `collect_raw_data(checkpoint)`: 데이터 수집
  - `get_channel()`: 채널 정보 반환
- **`truth_social.py`**: Truth Social RSS 피드 수집기 (구현 완료)
  - RSS 피드 파싱 및 데이터 구조화
  - HTML 태그 제거 및 콘텐츠 필터링
  - URL 전용 포스트, 리트윗 필터링
- **`dummy.py`**: 테스트용 Dummy Collector

#### `infrastructure/`
- **`message_queue.py`**: Redis Streams 클라이언트
  - 수집된 데이터를 다음 레이어로 발행
  - 스트림명: `trump-scan:data-collection:raw-data`
- **`state_store.py`**: Checkpoint 관리 (Redis)
  - 마지막 수집 시점 저장/조회
  - 중복 수집 방지
- **`database.py`**: 원본 데이터 저장 (Oracle DB)
  - Wallet 기반 인증
  - 수집 데이터 영구 저장

#### `models/`
- **`channel.py`**: Channel Enum
  - 수집 채널 타입 정의 (TRUTH_SOCIAL, DUMMY)
- **`raw_data.py`**: RawData Pydantic 모델
  - 수집 데이터 구조 정의 및 검증
  - 필드: id, content, link, published_at, channel
  - JSON 직렬화 지원

#### `config/`
- **`database.py`**: Oracle DB 연결 설정 (gitignore)
  - username, password, dsn, wallet 정보
- **`redis.py`**: Redis 연결 설정 (gitignore)
  - host, port, db 정보
- **`scheduler.py`**: 스케줄러 설정 (git 관리)
  - 수집 주기, job ID/이름 등
  - 기본 주기: 5분 (설정 변경 가능)
- **`*.example.py`**: 설정 템플릿 파일

#### `orchestrator.py`
- **책임**: 전체 수집 흐름 조율
  - Collector 등록 및 관리
  - 인프라 컴포넌트 관리 (StateStore, Database, MessageQueue)
  - Checkpoint 조회 → 수집 → 저장 → 발행 → Checkpoint 저장 흐름 제어
- **스케줄링**: APScheduler 기반
  - 설정: `config/scheduler.py`에서 관리
  - 즉시 실행 + 주기적 실행
  - 우아한 종료: SIGINT/SIGTERM 시그널 처리

#### `logger.py`
- **구조화된 로깅**: structlog 기반
  - 포맷: `YYYY-MM-DD HH:MM:SS [LEVEL][logger] message key=value`
  - 컨텍스트 정보 자동 추가

---

## 🛠️ 기술 스택

### 언어 및 런타임
- **Python 3.11+**

### 핵심 라이브러리

| 라이브러리 | 용도 | 버전 |
|-----------|------|------|
| **structlog** | 구조화된 로깅 | >=23.0.0 |
| **redis** | Redis 연결 (Streams, KV) | >=5.0.0 |
| **httpx** | HTTP 클라이언트 | >=0.24.0 |
| **feedparser** | RSS 피드 파싱 | >=6.0.0 |
| **beautifulsoup4** | HTML 파싱 | >=4.12.0 |
| **pydantic** | 데이터 검증 및 모델링 | >=2.0.0 |
| **oracledb** | Oracle DB 연결 | >=2.0.0 |
| **pytest** | 테스팅 | >=7.0.0 |
| **APScheduler** | 스케줄링 | >=3.10.0 |

### 인프라 의존성

| 서비스 | 용도 |
|--------|------|
| **Redis** | Message Queue + State Store |
| **Oracle DB** | 원본 데이터 저장 |