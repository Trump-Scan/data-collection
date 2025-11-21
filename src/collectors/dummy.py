"""
DummyCollector: 테스트용 Collector

BaseCollector 동작 확인을 위한 더미 구현체입니다.
"""
from typing import List, Dict, Any, Optional
from src.collectors.base import BaseCollector


class DummyCollector(BaseCollector):
    """테스트용 더미 Collector"""

    def collect_raw_data(self, checkpoint: Optional[str]) -> List[Dict[str, Any]]:
        """
        더미 데이터 반환

        Args:
            checkpoint: 마지막으로 수집한 위치 정보

        Returns:
            더미 데이터 리스트
        """
        self.logger.info("더미 데이터 수집 중", checkpoint=checkpoint)

        # 더미 데이터 생성
        dummy_data = [
            {"id": "1", "content": "Test message 1", "timestamp": "2025-11-21 10:00:00"},
            {"id": "2", "content": "Test message 2", "timestamp": "2025-11-21 11:00:00"},
        ]

        self.logger.info("더미 데이터 수집 완료", count=len(dummy_data))
        return dummy_data

    def get_channel_name(self) -> str:
        """
        채널 이름 반환

        Returns:
            채널 이름
        """
        return "dummy"
