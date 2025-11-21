"""
데이터 수집 레이어 진입점

트럼프 대통령 발언을 여러 채널에서 수집하는 애플리케이션의 시작점입니다.
"""
from src.logger import setup_logging, get_logger
from src.orchestrator import Orchestrator


def main():
    """애플리케이션 시작점"""
    # 로깅 설정
    setup_logging(level="DEBUG")
    logger = get_logger(__name__)

    logger.info("Data Collection Layer Started")

    # Orchestrator 생성
    orchestrator = Orchestrator()


if __name__ == "__main__":
    main()
