"""
데이터 수집 레이어 진입점

트럼프 대통령 발언을 여러 채널에서 수집하는 애플리케이션의 시작점입니다.
"""
import signal
import sys
from src.logger import setup_logging, get_logger
from src.orchestrator import Orchestrator
from src.collectors.truth_social import TruthSocialCollector
from src.infrastructure.state_store import StateStore
from src.infrastructure.database import Database
from src.infrastructure.message_queue import MessageQueue


def main():
    """애플리케이션 시작점"""
    # 로깅 설정
    setup_logging(level="DEBUG")
    logger = get_logger(__name__)

    logger.info("Data Collection Layer Started")

    # 인프라 컴포넌트 생성
    state_store = StateStore()
    database = Database()
    message_queue = MessageQueue()

    # Collector 등록
    collectors = [
        TruthSocialCollector(),
        # NewsCollector(),  # TODO: 향후 추가
    ]

    # Orchestrator 생성
    orchestrator = Orchestrator(
        collectors=collectors,
        state_store=state_store,
        database=database,
        message_queue=message_queue,
    )

    # 시그널 핸들러 등록 (우아한 종료)
    def signal_handler(sig, frame):
        logger.info("종료 시그널 수신, 우아하게 종료합니다...")
        orchestrator.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 스케줄러 시작
    logger.info("스케줄러 시작")
    orchestrator.start()


if __name__ == "__main__":
    main()
