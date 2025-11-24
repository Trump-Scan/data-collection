"""
StateStore: Checkpoint 저장/조회

Redis를 사용하여 각 Collector의 마지막 수집 위치(Checkpoint)를 관리합니다.
"""
from typing import Optional
from datetime import datetime
import redis
from src.logger import get_logger
from src.models.channel import Channel
from config.redis import REDIS_CONFIG


class StateStore:
    """Checkpoint 관리 클래스"""

    def __init__(self):
        """StateStore 초기화"""
        self.logger = get_logger(__name__)

        # Redis 설정 로드
        host = REDIS_CONFIG["host"]
        port = REDIS_CONFIG["port"]
        db = REDIS_CONFIG["db"]
        password = REDIS_CONFIG.get("password")  # 선택적

        # Redis 클라이언트 생성
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )

        # 연결 테스트
        try:
            self.redis_client.ping()
            self.logger.info("Redis 연결 성공", host=host, port=port, db=db)
        except redis.ConnectionError as e:
            self.logger.error("Redis 연결 실패", host=host, port=port, error=str(e))
            raise

    def get_checkpoint(self, channel: Channel) -> Optional[datetime]:
        """
        채널의 마지막 Checkpoint 조회

        Args:
            channel: 채널

        Returns:
            Checkpoint datetime (없으면 None)
        """
        key = f"checkpoint:{channel}"
        checkpoint_str = self.redis_client.get(key)

        if checkpoint_str:
            try:
                checkpoint = datetime.fromisoformat(checkpoint_str.replace('Z', '+00:00'))
                self.logger.debug("Checkpoint 조회", channel=channel, checkpoint=checkpoint)
                return checkpoint
            except (ValueError, AttributeError) as e:
                self.logger.warning("Checkpoint 파싱 실패", channel=channel, checkpoint=checkpoint_str, error=str(e))
                return None
        else:
            self.logger.debug("Checkpoint 없음 (첫 수집)", channel=channel)
            return None

    def save_checkpoint(self, channel: Channel, checkpoint: datetime):
        """
        채널의 Checkpoint 저장

        Args:
            channel: 채널
            checkpoint: 저장할 Checkpoint datetime
        """
        key = f"checkpoint:{channel}"
        checkpoint_str = checkpoint.isoformat()
        self.redis_client.set(key, checkpoint_str)
        self.logger.debug("Checkpoint 저장", channel=channel, checkpoint=checkpoint)
