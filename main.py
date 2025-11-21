"""
데이터 수집 레이어 진입점

트럼프 대통령 발언을 여러 채널에서 수집하는 애플리케이션의 시작점입니다.
"""
from src.logger import setup_logging, get_logger
from src.orchestrator import Orchestrator
from src.collectors.dummy import DummyCollector


def main():
    """애플리케이션 시작점"""
    # 로깅 설정
    setup_logging(level="DEBUG")
    logger = get_logger(__name__)

    logger.info("Data Collection Layer Started")

    # Collector 등록
    collectors = [
        DummyCollector(),
        # TruthSocialCollector(),  # TODO: Step 5에서 추가
        # NewsCollector(),  # TODO: 향후 추가
    ]

    # Orchestrator 생성 및 실행
    orchestrator = Orchestrator(collectors=collectors)
    orchestrator.run()


if __name__ == "__main__":
    main()
