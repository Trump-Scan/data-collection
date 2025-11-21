"""
TruthSocialCollector: Truth Social RSS 피드 수집기

Trump's Truth Social 플랫폼에서 발언을 수집합니다.
"""
from typing import List, Dict, Any, Optional
from src.collectors.base import BaseCollector


class TruthSocialCollector(BaseCollector):
    """Truth Social RSS 피드 수집 Collector"""

    def collect_raw_data(self, checkpoint: Optional[str]) -> List[Dict[str, Any]]:
        """
        Truth Social RSS 피드에서 데이터 수집

        Args:
            checkpoint: 마지막으로 수집한 위치 정보

        Returns:
            수집된 원본 데이터 리스트
        """
        self.logger.info("Truth Social 데이터 수집 시작", checkpoint=checkpoint)

        # TODO: Step 7에서 실제 RSS 피드 호출 및 파싱 구현 예정
        # 지금은 빈 리스트 반환
        collected_data = []

        self.logger.info("Truth Social 데이터 수집 완료", count=len(collected_data))
        return collected_data

    def get_channel_name(self) -> str:
        """
        채널 이름 반환

        Returns:
            채널 이름
        """
        return "truth_social"
