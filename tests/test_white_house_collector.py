"""
WhiteHouseCollector 테스트
"""

import pytest
from datetime import datetime, timezone
from src.collectors.white_house import WhiteHouseCollector
from src.models.channel import Channel


class TestWhiteHouseCollector:
    """WhiteHouseCollector 테스트 클래스"""

    @pytest.fixture
    def collector(self):
        """WhiteHouseCollector 인스턴스 생성"""
        return WhiteHouseCollector()

    def test_get_channel(self, collector):
        """채널 반환 테스트"""
        assert collector.get_channel() == Channel.WHITE_HOUSE
        assert collector.get_channel().value == "white_house"

    def test_collect_raw_data_real(self, collector):
        """실제 RSS 피드 수집 테스트 (네트워크 필요)"""
        result = collector.collect_raw_data(checkpoint=None)

        assert result is not None
        assert isinstance(result, list)

        if len(result) > 0:
            from src.models.raw_data import RawData

            assert isinstance(result[0], RawData)
            assert result[0].content is not None
            assert result[0].link is not None
            assert result[0].published_at is not None
            assert result[0].channel == Channel.WHITE_HOUSE

            # 정렬 검증: 오름차순 (옛날 데이터가 먼저)
            for i in range(len(result) - 1):
                assert result[i].published_at <= result[i + 1].published_at

    def test_parse_published_date(self, collector):
        """날짜 파싱 테스트"""
        import time
        from types import SimpleNamespace

        # Mock entry with published_parsed
        entry = SimpleNamespace()
        entry.published_parsed = time.strptime(
            "2026-03-05 12:00:00", "%Y-%m-%d %H:%M:%S"
        )

        result = collector._parse_published_date(entry)

        assert result is not None
        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc
        assert result.year == 2026
        assert result.month == 3
        assert result.day == 5

    def test_clean_html(self, collector):
        """HTML 정제 테스트"""
        html = "<p>Hello  <b>World</b></p>"
        result = collector._clean_html(html)
        assert result == "Hello World"
