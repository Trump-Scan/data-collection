"""
BaseCollector: Collector 인터페이스

각 채널에서 데이터를 수집하는 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.logger import get_logger


class BaseCollector(ABC):
    """
    Collector 인터페이스

    책임: 특정 채널에서 데이터 수집만 담당
    - collect_raw_data(): 실제 데이터 수집 로직 (추상 메서드)
    - get_channel_name(): 채널 이름 반환 (추상 메서드)
    """

    def __init__(self):
        """BaseCollector 초기화"""
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def collect_raw_data(self, checkpoint: Optional[str]) -> List[Dict[str, Any]]:
        """
        실제 데이터 수집 로직 (하위 클래스에서 구현)

        Args:
            checkpoint: 마지막으로 수집한 위치 정보

        Returns:
            수집된 원본 데이터 리스트
        """
        pass

    @abstractmethod
    def get_channel_name(self) -> str:
        """
        채널 이름 반환 (하위 클래스에서 구현)

        Returns:
            채널 이름 (예: "truth_social", "news")
        """
        pass
