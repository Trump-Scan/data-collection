"""
Orchestrator: Collector 조율자

여러 Collector를 등록하고 관리하며, 전체 수집 흐름을 조율합니다.
"""
from typing import List
from apscheduler.schedulers.blocking import BlockingScheduler
from src.logger import get_logger
from config.scheduler import SCHEDULER_CONFIG


class Orchestrator:
    """
    Collector 조율 및 관리 클래스

    책임:
    - Collector 관리
    - 전체 수집 흐름 제어 (checkpoint 조회 → 수집 → 저장 → 발행 → checkpoint 저장)
    """

    def __init__(self, collectors: List = None, state_store=None, database=None, message_queue=None):
        """
        Orchestrator 초기화

        Args:
            collectors: BaseCollector를 상속한 Collector 인스턴스 리스트
            state_store: Checkpoint 저장/조회 인프라
            database: 원본 데이터 저장 인프라
            message_queue: 메시지 발행 인프라
        """
        self.logger = get_logger(__name__)
        self.collectors: List = collectors if collectors else []
        self.state_store = state_store
        self.database = database
        self.message_queue = message_queue
        self.scheduler = BlockingScheduler()

        # 등록된 Collector 로깅
        for collector in self.collectors:
            channel = collector.get_channel()
            self.logger.info("Collector 등록", channel=channel)

        self.logger.info("Orchestrator 초기화 완료", collectors_count=len(self.collectors))

    def run(self):
        """
        등록된 모든 Collector의 수집 작업 실행

        각 Collector에 대해:
        1. Checkpoint 조회
        2. collect_raw_data() 호출
        3. 데이터 저장 (Database)
        4. 메시지 발행 (Message Queue)
        5. Checkpoint 저장
        """
        self.logger.info("수집 작업 시작", collectors_count=len(self.collectors))

        for collector in self.collectors:
            channel = collector.get_channel()

            try:
                self.logger.info("Collector 실행 시작", channel=channel)

                # 1. Checkpoint 조회
                checkpoint = self.state_store.get_checkpoint(channel)

                # 2. 데이터 수집
                collected_data = collector.collect_raw_data(checkpoint)

                # 3. 데이터가 있으면 저장 및 발행
                if collected_data:
                    self.logger.info("수집된 데이터 있음", channel=channel, count=len(collected_data))

                    # 3-1. 건별로 Database 저장 및 Message Queue 발행
                    for raw_data in collected_data:
                        # Database 저장 (ID 할당됨)
                        saved_data = self.database.save_raw_data(raw_data)

                        # Message Queue 발행
                        self.message_queue.publish(saved_data)

                    self.logger.info("Database 저장 및 Message Queue 발행 완료", channel=channel, count=len(collected_data))

                    # 3-2. Checkpoint 저장 (가장 최근 데이터의 published_at)
                    new_checkpoint = max(data.published_at for data in collected_data)
                    self.state_store.save_checkpoint(channel, new_checkpoint)
                    self.logger.info("Checkpoint 저장 완료", channel=channel, checkpoint=new_checkpoint)
                else:
                    self.logger.info("수집된 데이터 없음", channel=channel)

                self.logger.info("Collector 실행 완료", channel=channel)

            except Exception as e:
                self.logger.error("Collector 실행 실패", channel=channel, error=str(e))

        self.logger.info("수집 작업 완료")

    def start(self):
        """
        스케줄러 시작 및 주기적 수집 실행

        5분마다 수집 작업을 실행합니다.
        """
        # 즉시 한 번 실행
        self.logger.info("초기 수집 작업 실행")
        self.run()

        # 스케줄 등록 (설정 파일 사용)
        self.scheduler.add_job(
            func=self.run,
            trigger=SCHEDULER_CONFIG['trigger'],
            minutes=SCHEDULER_CONFIG['minutes'],
            id=SCHEDULER_CONFIG['id'],
            name=SCHEDULER_CONFIG['name']
        )

        self.logger.info(
            "스케줄러 시작됨",
            interval_minutes=SCHEDULER_CONFIG['minutes'],
            job_name=SCHEDULER_CONFIG['name']
        )

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.logger.info("스케줄러 종료")

    def shutdown(self):
        """스케줄러 우아한 종료"""
        self.logger.info("스케줄러 종료 중...")
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
        self.logger.info("스케줄러 종료 완료")
