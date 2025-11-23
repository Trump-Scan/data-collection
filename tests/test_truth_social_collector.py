"""
TruthSocialCollector 테스트
"""
import pytest
from datetime import datetime
from src.collectors.truth_social import TruthSocialCollector
from src.models.channel import Channel


class TestTruthSocialCollector:
    """TruthSocialCollector 테스트 클래스"""

    @pytest.fixture
    def collector(self):
        """TruthSocialCollector 인스턴스 생성"""
        return TruthSocialCollector()

    def test_get_channel(self, collector):
        """채널 반환 테스트"""
        assert collector.get_channel() == Channel.TRUTH_SOCIAL
        assert collector.get_channel().value == "truth_social"

    def test_collect_raw_data_no_checkpoint(self, collector):
        """checkpoint 없이 실제 RSS 피드 수집 테스트"""
        result = collector.collect_raw_data(checkpoint=None)

        # 실제 데이터가 수집되었는지 확인
        assert result is not None
        assert isinstance(result, list)

        # 데이터가 있으면 구조 검증
        if len(result) > 0:
            from src.models.raw_data import RawData
            assert isinstance(result[0], RawData)
            assert result[0].content is not None
            assert result[0].link is not None
            assert result[0].published_at is not None
            assert result[0].channel == Channel.TRUTH_SOCIAL

    def test_parse_published_date_with_published_parsed(self, collector):
        """published_parsed를 사용한 날짜 파싱 테스트"""
        import time
        from types import SimpleNamespace

        # Mock entry with published_parsed
        entry = SimpleNamespace()
        entry.published_parsed = time.strptime("2025-11-23 12:00:00", "%Y-%m-%d %H:%M:%S")

        result = collector._parse_published_date(entry)

        assert result is not None
        assert isinstance(result, datetime)

    def test_parse_published_date_no_date(self, collector):
        """날짜 정보가 없는 경우 테스트"""
        from types import SimpleNamespace

        entry = SimpleNamespace()
        result = collector._parse_published_date(entry)

        assert result is None
