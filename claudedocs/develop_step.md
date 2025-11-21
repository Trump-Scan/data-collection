# 데이터 수집 레이어 개발 단계

데이터 흐름 순서에 따라 점진적으로 개발합니다. 각 단계는 해당 단계에 필요한 작업만 수행합니다.

---

## 데이터 흐름

```
main.py 
  ↓
Orchestrator 
  ↓
BaseCollector.collect() [Template Method]
  ├─ State Store에서 Checkpoint 조회
  ├─ collect_raw_data(checkpoint) 호출 ← TruthSocialCollector가 구현
  ├─ Database에 저장
  ├─ Message Queue 발행
  └─ State Store에 Checkpoint 저장
  
TruthSocialCollector.collect_raw_data():
  ├─ API 호출 (RSS 피드)
  └─ 데이터 파싱
```

---

## Step 1: 진입점 생성

**목적:** 애플리케이션 시작점 마련

**작업:**
- `main.py` 파일 생성
- 간단한 print 문으로 시작 확인

**확인:**
- `python main.py` 실행 시 print 출력 확인

---

## Step 2: 구조화된 로깅 추가

**목적:** 실행 흐름 및 에러 추적

**작업:**
- structlog 사용 (requirements.txt, venv 설정)
- `src/logger.py` 모듈 생성 (커스텀 포맷)
- `main.py`에서 logger 사용
- 로그 포맷: `YYYY-MM-DD HH:MM:SS [LEVEL][logger] message`

**확인:**
- 로그 출력 확인

---

## Step 3: Orchestrator 기본 골격

**목적:** Collector들을 관리할 조율자 구조 마련

**작업:**
- `src/orchestrator.py` 생성
- Orchestrator 클래스 정의
  - 생성자에서 collectors 리스트 받아서 초기화
  - `run()` 메서드: 등록된 Collector의 collect() 호출
- `main.py`에서 collectors 변수로 관리

**확인:**
- Orchestrator 초기화 및 실행 로그 확인

---

## Step 4: BaseCollector 골격 (Template Method)

**목적:** 모든 Collector가 따라야 할 공통 흐름 정의

**작업:**
- `src/collectors/base.py` 생성
- BaseCollector 추상 클래스 정의
  - `collect()` Template Method (로그만 출력)
  - `collect_raw_data(checkpoint)` 추상 메서드
  - `get_channel_name()` 추상 메서드
- `src/collectors/dummy.py` 생성 (테스트용)
  - DummyCollector 구현
- `main.py`에서 DummyCollector 테스트

**확인:**
- DummyCollector가 Orchestrator를 통해 실행되는지 확인

---

## Step 5: TruthSocialCollector 기본 구조

**목적:** Truth Social 수집기의 뼈대 구현

**작업:**
- `src/collectors/truth_social.py` 생성
- TruthSocialCollector 클래스 정의 (BaseCollector 상속)
- `collect_raw_data(checkpoint)` 빈 구현 (빈 리스트 반환)
- `get_channel_name()` 구현 ("truth_social" 반환)
- Orchestrator에 Collector 인스턴스 등록 (state_store=None 등으로 전달)
- 로그 추가

**확인:**
- TruthSocialCollector 인스턴스 생성 가능
- Orchestrator에서 Collector 참조 가능
- `collect()` 호출 시 로그 출력 확인

---

## Step 6: State Store 구현

**목적:** Checkpoint 저장/조회 기능 구현

**작업:**
- `src/infrastructure/state_store.py` 생성
- StateStore 클래스 정의
- Redis 연결 설정
- `get_checkpoint(channel_name)` 메서드 구현
- `save_checkpoint(channel_name, checkpoint)` 메서드 구현
- 로그 추가
- `requirements.txt` 생성 및 redis 라이브러리 추가

**확인:**
- Redis 연결 성공
- Checkpoint 저장/조회 동작 확인

---

## Step 7: RSS 피드 API 호출 및 파싱

**목적:** Truth Social RSS 데이터 실제 수집

**작업:**
- `TruthSocialCollector.collect_raw_data(checkpoint)` 메서드 실제 구현
- httpx를 사용한 RSS 피드 API 호출
- feedparser를 사용한 RSS 파싱
- checkpoint 이후 데이터만 필터링 (간단한 시간 비교)
- 수집된 데이터를 구조화 (딕셔너리 리스트)
- 로그 추가
- `requirements.txt`에 httpx, feedparser, pytest 추가
- **테스트 작성**: `tests/test_truth_social_collector.py` 생성
  - `collect_raw_data()` 단위 테스트
  - HTTP 응답 mock 사용
  - 파싱 결과 검증

**확인:**
- RSS 피드 호출 성공
- 파싱된 데이터 구조 확인
- 로그로 수집된 항목 수 확인
- **테스트 실행**: `pytest tests/test_truth_social_collector.py`
- 테스트 통과 확인

---

## Step 8: Database 구현

**목적:** 원본 데이터 영구 저장

**작업:**
- `src/infrastructure/database.py` 생성
- Database 클래스 정의
- Oracle DB 연결 설정
- `save_raw_data(raw_data_list)` 메서드 구현
  - `raw_data` 테이블에 INSERT
  - ID 생성 및 반환
- 로그 추가
- `requirements.txt`에 oracledb 추가

**확인:**
- DB 연결 성공
- 테스트 데이터 저장 및 조회 가능

---

## Step 9: Message Queue 구현

**목적:** 다음 레이어로 데이터 전달

**작업:**
- `src/infrastructure/message_queue.py` 생성
- MessageQueue 클래스 정의
- Redis Streams 연결
- `publish(message)` 메서드 구현
  - 메시지 페이로드 구조화 (ID, 원본 데이터, 채널 정보)
  - Redis Streams에 발행
- 로그 추가

**확인:**
- Redis Streams에 메시지 발행 성공
- redis-cli로 메시지 내용 확인 가능

---

## Step 10: BaseCollector Template Method 완성

**목적:** 전체 수집 흐름 통합

**작업:**
- BaseCollector의 `collect()` 메서드 완성
  1. state_store.get_checkpoint(channel_name) 호출
  2. collect_raw_data(checkpoint) 호출
  3. 수집된 데이터가 있으면:
     - database.save_raw_data() 호출
     - message_queue.publish() 호출
     - state_store.save_checkpoint() 호출
  4. 수집 결과 로그 출력
- Orchestrator에서 Collector 생성 시 state_store, database, message_queue 주입
- 로그 추가

**확인:**
- `collect()` 호출 시 전체 흐름 동작
- DB에 데이터 저장 확인
- Redis Streams에 메시지 발행 확인
- Checkpoint 저장 확인

---

## Step 11: Orchestrator와 Collector 연결

**목적:** Orchestrator가 실제로 Collector 실행

**작업:**
- StateStore, Database, MessageQueue 인스턴스를 Orchestrator에서 생성
- Collector 생성 시 인프라 컴포넌트 주입
- Orchestrator에 `run()` 메서드 구현
  - 등록된 Collector의 `collect()` 호출
  - 에러 처리 (try-except)
- `main.py`에서 `orchestrator.run()` 호출
- 로그 추가

**확인:**
- `python main.py` 실행 시 전체 수집 프로세스 동작
- 데이터가 수집되어 DB에 저장되고 메시지 발행됨

---

## Step 12: 스케줄링 추가

**목적:** 주기적으로 자동 수집

**작업:**
- APScheduler를 사용한 스케줄링 구현
- Orchestrator에 스케줄러 추가
- 수집 주기 설정 (5분)
- 우아한 종료 처리 (Ctrl+C 시)
- 로그 추가
- `requirements.txt`에 APScheduler 추가

**확인:**
- 5분마다 자동으로 수집 실행
- Ctrl+C로 안전하게 종료
- 로그로 스케줄링 확인

---

## Step 13: 설정 관리

**목적:** 하드코딩된 값을 설정으로 분리

**작업:**
- `src/config.py` 생성
- 환경 변수에서 값 로드
- Redis, Oracle, 수집 주기 등 설정 항목 정의
- 각 모듈에서 config import하여 사용
- `.env.example` 파일 생성
- `requirements.txt`에 python-dotenv 추가

**확인:**
- 환경 변수 변경 시 코드 수정 없이 동작 변경 가능
- 로그에 사용 중인 설정 값 출력

---

## Step 14: 데이터 검증

**목적:** 수집/파싱된 데이터의 품질 보장

**작업:**
- Pydantic 모델 정의 (RawData)
- 필수 필드 검증 (content, channel, published_at 등)
- TruthSocialCollector에서 데이터 검증 추가
- 검증 실패 시 로그 남기고 스킵
- `requirements.txt`에 pydantic 추가

**확인:**
- 올바른 데이터만 반환됨
- 잘못된 데이터는 로그에 기록되고 스킵

---

## Step 15: 에러 처리 및 재시도

**목적:** 일시적 오류 대응

**작업:**
- 네트워크 에러 처리 (API 호출 실패)
  - TruthSocialCollector의 collect_raw_data()에 try-except
- DB 연결 에러 처리
  - Database 클래스에 재연결 로직
- Redis 연결 에러 처리
  - StateStore, MessageQueue에 재연결 로직
- 재시도 로직 추가 (exponential backoff)
- 최대 재시도 횟수 설정
- 로그 추가
- `requirements.txt`에 tenacity 추가

**확인:**
- 일시적 오류 발생 시 자동 재시도
- 재시도 실패 시 로그 남기고 다음 주기에 재시도

---

## 단계별 개발 원칙

1. **점진적 개발**: 각 단계는 이전 단계에 의존
2. **필요한 것만**: 해당 단계에 필요한 파일/라이브러리만 추가
3. **동작 확인**: 각 단계마다 실행하여 동작 확인
4. **커밋 단위**: 각 단계를 완료하면 커밋
5. **테스트 작성**: 필요 시 간단한 테스트 추가 (선택)

---

## 다음 단계

Step 15 완료 후:
- News Collector 추가 (동일한 패턴으로 개발)
- 성능 모니터링 추가
- 문서 업데이트