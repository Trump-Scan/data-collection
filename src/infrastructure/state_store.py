"""
StateStore: Checkpoint 저장/조회

Redis를 사용하여 각 Collector의 마지막 수집 위치(Checkpoint)를 관리합니다.
"""
from typing import Optional
import redis
from src.logger import get_logger


class StateStore:
    """Checkpoint 관리 클래스"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """
        StateStore 초기화

        Args:
            host: Redis 호스트
            port: Redis 포트
            db: Redis 데이터베이스 번호
        """
        self.logger = get_logger(__name__)
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

        # 연결 테스트
        try:
            self.redis_client.ping()
            self.logger.info("Redis 연결 성공", host=host, port=port, db=db)
        except redis.ConnectionError as e:
            self.logger.error("Redis 연결 실패", host=host, port=port, error=str(e))
            raise

    def get_checkpoint(self, channel_name: str) -> Optional[str]:
        """
        채널의 마지막 Checkpoint 조회

        Args:
            channel_name: 채널 이름 (예: "truth_social")

        Returns:
            Checkpoint 값 (없으면 None)
        """
        key = f"checkpoint:{channel_name}"
        checkpoint = self.redis_client.get(key)

        if checkpoint:
            self.logger.debug("Checkpoint 조회", channel=channel_name, checkpoint=checkpoint)
        else:
            self.logger.debug("Checkpoint 없음 (첫 수집)", channel=channel_name)

        return checkpoint

    def save_checkpoint(self, channel_name: str, checkpoint: str):
        """
        채널의 Checkpoint 저장

        Args:
            channel_name: 채널 이름 (예: "truth_social")
            checkpoint: 저장할 Checkpoint 값
        """
        key = f"checkpoint:{channel_name}"
        self.redis_client.set(key, checkpoint)
        self.logger.debug("Checkpoint 저장", channel=channel_name, checkpoint=checkpoint)
