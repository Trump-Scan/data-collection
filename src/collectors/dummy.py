"""
DummyCollector: 테스트용 Collector

BaseCollector 동작 확인을 위한 더미 구현체입니다.
"""
from typing import List, Optional
from datetime import datetime, timezone
from src.collectors.base import BaseCollector
from src.models.channel import Channel
from src.models.raw_data import RawData


class DummyCollector(BaseCollector):
    """테스트용 더미 Collector"""

    def collect_raw_data(self, checkpoint: Optional[datetime]) -> List[RawData]:
        """
        더미 데이터 반환

        Args:
            checkpoint: 마지막으로 수집한 시간

        Returns:
            더미 데이터 리스트
        """
        self.logger.info("더미 데이터 수집 중", checkpoint=checkpoint)

        # 더미 데이터 생성
        dummy_data = [
            RawData(
                content="Test message 1",
                link="https://example.com/1",
                published_at=datetime(2025, 11, 21, 10, 0, 0, tzinfo=timezone.utc),
                channel=self.get_channel()
            ),
            RawData(
                content="Test message 2",
                link="https://example.com/2",
                published_at=datetime(2025, 11, 21, 11, 0, 0, tzinfo=timezone.utc),
                channel=self.get_channel()
            ),
        ]

        self.logger.info("더미 데이터 수집 완료", count=len(dummy_data))
        return dummy_data

    def get_channel(self) -> Channel:
        """
        채널 반환

        Returns:
            Channel enum
        """
        return Channel.DUMMY
