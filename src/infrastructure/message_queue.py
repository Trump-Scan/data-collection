"""
MessageQueue: Redis Streams 메시지 큐

수집된 데이터를 다음 레이어로 전달하는 메시지 큐입니다.
"""
import json
import redis
from src.logger import get_logger
from src.models.raw_data import RawData
from config.redis import REDIS_CONFIG


class MessageQueue:
    """Redis Streams 기반 메시지 큐"""

    def __init__(self):
        """MessageQueue 초기화"""
        self.logger = get_logger(__name__)

        # Redis 설정 로드
        host = REDIS_CONFIG["host"]
        port = REDIS_CONFIG["port"]
        db = REDIS_CONFIG["db"]

        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.stream_name = "trump-scan:data-collection:raw-data"

        # 연결 테스트
        try:
            self.redis_client.ping()
            self.logger.info("MessageQueue 연결 성공", host=host, port=port, db=db)
        except redis.ConnectionError as e:
            self.logger.error("MessageQueue 연결 실패", error=str(e))
            raise

    def publish(self, raw_data: RawData) -> str:
        """
        메시지 발행

        Args:
            raw_data: 발행할 RawData 객체

        Returns:
            발행된 메시지 ID
        """
        try:
            # JSON 직렬화 (Pydantic model_dump 사용)
            message_json = json.dumps(raw_data.to_dict(), ensure_ascii=False)

            # Redis Streams에 발행
            message_id = self.redis_client.xadd(
                self.stream_name,
                {"data": message_json}
            )

            self.logger.debug(
                "메시지 발행 완료",
                message_id=message_id,
                raw_data_id=raw_data.id,
                channel=raw_data.channel.value
            )

            return message_id

        except redis.RedisError as e:
            self.logger.error("메시지 발행 실패", error=str(e), raw_data_id=raw_data.id)
            raise
        except Exception as e:
            self.logger.error(
                "메시지 발행 중 예외 발생",
                error=str(e),
                error_type=type(e).__name__,
                raw_data_id=raw_data.id
            )
            raise
