"""
구조화된 로깅 설정

structlog를 사용하여 구조화된 로그를 제공합니다.
JSON 형식으로 출력하여 나중에 분석하기 쉽게 합니다.
"""
import logging
import sys
import structlog


def setup_logging(level: str = "INFO"):
    """
    structlog 로깅 설정

    Args:
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # 표준 logging 레벨 설정
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper())
    )

    # 커스텀 포맷터 정의
    class CustomConsoleRenderer:
        """커스텀 로그 포맷: YYYY-MM-DD HH:MM:SS [level][logger] message"""

        def __call__(self, logger, method_name, event_dict):
            timestamp = event_dict.pop("timestamp", "")
            level = event_dict.pop("level", "info").upper()
            logger_name = event_dict.pop("logger", "")
            event = event_dict.pop("event", "")

            # 기본 로그 라인
            log_line = f"{timestamp} [{level}][{logger_name}] {event}"

            # 추가 컨텍스트가 있으면 key=value 형식으로 추가
            if event_dict:
                extras = " ".join(f"{k}={v}" for k, v in event_dict.items())
                log_line = f"{log_line} {extras}"

            return log_line

    # structlog 설정
    structlog.configure(
        processors=[
            # 로그 레벨 추가
            structlog.stdlib.add_log_level,
            # 로거 이름 추가
            structlog.stdlib.add_logger_name,
            # 타임스탬프 추가 (간결한 포맷)
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            # 스택 정보 추가 (에러 발생 시)
            structlog.processors.StackInfoRenderer(),
            # 예외 정보 포매팅
            structlog.processors.format_exc_info,
            # 커스텀 포맷터
            CustomConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None):
    """
    로거 인스턴스 생성

    Args:
        name: 로거 이름 (보통 __name__ 사용)

    Returns:
        structlog.BoundLogger: 구조화된 로거 인스턴스
    """
    return structlog.get_logger(name)
