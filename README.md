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
| **Truth Social** | RSS 피드 API 호출 | `https://trumpstruth.org/feed` | 5분 | ✅ 우선 구현 |
| **뉴스** | 웹 크롤링 | 주요 뉴스 사이트 | 10분 | 📋 예정 |

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
│   │   ├── truth_social.py     # Truth Social Collector
│   │   └── news.py             # (향후) News Collector
│   │
│   ├── infrastructure/          # 인프라 레이어
│   │   ├── __init__.py
│   │   ├── message_queue.py    # Redis Streams 클라이언트
│   │   ├── state_store.py      # Redis Checkpoint 관리
│   │   └── database.py         # Oracle DB 연결
│   │
│   ├── orchestrator.py         # Collector 조율 및 스케줄링
│   └── config.py               # 설정 관리
│
├── tests/
├── requirements.txt
└── main.py                     # 진입점
```

### 주요 컴포넌트 설명

#### `collectors/base.py`
- Collector 인터페이스
- 책임: 데이터 수집만 담당
- 공통 인터페이스: `collect_raw_data(checkpoint)`, `get_channel_name()`

#### `collectors/truth_social.py`
- Truth Social RSS 피드 수집 구현
- 첫 번째 구현 대상

#### `infrastructure/`
- Redis Streams: 다음 레이어로 메시지 발행
- State Store: Checkpoint 저장/조회 (Redis)
- Database: 원본 데이터 저장 (Oracle)

#### `orchestrator.py`
- 책임: 전체 수집 흐름 조율
- Collector 관리
- 인프라 컴포넌트 관리 (StateStore, Database, MessageQueue)
- Checkpoint 조회 → 수집 → 저장 → 발행 → Checkpoint 저장 흐름 제어
- 주기적 실행 스케줄링 (APScheduler)

---

## 🛠️ 기술 스택

### 언어 및 런타임
- **Python 3.11+**

### 핵심 라이브러리

| 라이브러리 | 용도 | 버전 |
|-----------|------|------|
| **httpx** | 비동기 HTTP 클라이언트 | latest |
| **feedparser** | RSS 피드 파싱 | latest |
| **pydantic** | 데이터 검증 및 모델링 | ^2.0 |
| **redis** | Redis 연결 (Streams, KV) | latest |
| **oracledb** | Oracle DB 연결 | latest |
| **APScheduler** | 스케줄링 | latest |
| **structlog** | 구조화된 로깅 | latest |

### 인프라 의존성

| 서비스 | 용도 | 접속 정보 |
|--------|------|----------|
| **Redis** | Message Queue + State Store | `localhost:6379` |
| **Oracle DB** | 원본 데이터 저장 | OCI 설정 참조 |