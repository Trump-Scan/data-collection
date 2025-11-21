"""
Orchestrator: Collector 조율자

여러 Collector를 등록하고 관리하며, 수집 작업을 조율합니다.
"""
from typing import List
from src.logger import get_logger


class Orchestrator:
    """Collector 조율 및 관리 클래스"""

    def __init__(self, collectors: List = None):
        """
        Orchestrator 초기화

        Args:
            collectors: BaseCollector를 상속한 Collector 인스턴스 리스트
        """
        self.logger = get_logger(__name__)
        self.collectors: List = collectors if collectors else []

        # 등록된 Collector 로깅
        for collector in self.collectors:
            collector_name = collector.__class__.__name__
            self.logger.info("Collector 등록", collector=collector_name)

        self.logger.info("Orchestrator 초기화 완료", collectors_count=len(self.collectors))
