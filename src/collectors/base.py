"""
BaseCollector: 모든 Collector의 기본 클래스

Template Method 패턴을 사용하여 수집 흐름을 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.logger import get_logger


class BaseCollector(ABC):
    """
    모든 Collector가 상속해야 하는 추상 기본 클래스

    Template Method 패턴:
    - collect(): 전체 수집 흐름을 제어하는 템플릿 메서드 (구체 메서드)
    - collect_raw_data(): 각 Collector가 구현해야 하는 실제 수집 로직 (추상 메서드)
    - get_channel_name(): 채널 이름 반환 (추상 메서드)
    """

    def __init__(self, state_store=None, database=None, message_queue=None):
        """
        BaseCollector 초기화

        Args:
            state_store: Checkpoint 저장/조회 인프라
            database: 원본 데이터 저장 인프라
            message_queue: 메시지 발행 인프라
        """
        self.state_store = state_store
        self.database = database
        self.message_queue = message_queue
        self.logger = get_logger(self.__class__.__name__)

    def collect(self):
        """
        전체 수집 흐름을 제어하는 Template Method

        흐름:
        1. Checkpoint 조회
        2. collect_raw_data() 호출 (하위 클래스 구현)
        3. 데이터 저장 (Database)
        4. 메시지 발행 (Message Queue)
        5. Checkpoint 저장
        """
        channel_name = self.get_channel_name()
        self.logger.info("수집 시작", channel=channel_name)

        # TODO: Step 10에서 실제 구현 예정
        # 지금은 로그만 출력
        self.logger.info("수집 완료", channel=channel_name, collected_count=0)

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
