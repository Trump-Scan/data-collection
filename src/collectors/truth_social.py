"""
TruthSocialCollector: Truth Social RSS 피드 수집기

Trump's Truth Social 플랫폼에서 발언을 수집합니다.
"""
from typing import List, Optional
from datetime import datetime
import httpx
import feedparser
from src.collectors.base import BaseCollector
from src.models.channel import Channel
from src.models.raw_data import RawData


class TruthSocialCollector(BaseCollector):
    """Truth Social RSS 피드 수집 Collector"""

    RSS_FEED_URL = "https://trumpstruth.org/feed"
    REQUEST_TIMEOUT = 30.0

    def collect_raw_data(self, checkpoint: Optional[datetime]) -> List[RawData]:
        """
        Truth Social RSS 피드에서 데이터 수집

        Args:
            checkpoint: 마지막으로 수집한 시간

        Returns:
            수집된 원본 데이터 리스트
        """
        self.logger.info("Truth Social 데이터 수집 시작", checkpoint=checkpoint)

        try:
            # RSS 피드 호출
            response = httpx.get(self.RSS_FEED_URL, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()

            self.logger.debug("RSS 피드 호출 성공", status_code=response.status_code)

            # RSS 파싱
            feed = feedparser.parse(response.text)

            if feed.bozo:
                self.logger.warning("RSS 파싱 경고", error=feed.bozo_exception)

            # checkpoint 이후 데이터 필터링
            collected_data = []

            for entry in feed.entries:
                # 발행 시간 파싱
                published_dt = self._parse_published_date(entry)

                if published_dt is None:
                    self.logger.warning("발행 시간 파싱 실패", entry_link=entry.get('link', 'Unknown'))
                    continue

                # checkpoint 이후 데이터만 수집
                if checkpoint and published_dt <= checkpoint:
                    continue

                # 데이터 구조화
                raw_data = RawData(
                    content=entry.get('summary', ''),
                    link=entry.get('link', ''),
                    published_at=published_dt,
                    channel=self.get_channel(),
                )

                collected_data.append(raw_data)
                self.logger.debug("데이터 수집", published_at=raw_data.published_at, link=raw_data.link)

            self.logger.info("Truth Social 데이터 수집 완료", count=len(collected_data))
            return collected_data


        except httpx.HTTPError as e:
            self.logger.error("HTTP 요청 실패", error=str(e), url=self.RSS_FEED_URL)
            return []
        except Exception as e:
            self.logger.error("데이터 수집 중 예외 발생", error=str(e), error_type=type(e).__name__)
            return []

    def _parse_published_date(self, entry) -> Optional[datetime]:
        """
        RSS entry의 발행 시간을 datetime으로 파싱

        Args:
            entry: feedparser의 entry 객체

        Returns:
            파싱된 datetime 객체 (UTC timezone-aware) 또는 None
        """
        from datetime import timezone

        # feedparser는 published_parsed (time.struct_time) 제공
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                import time
                timestamp = time.mktime(entry.published_parsed)
                # UTC timezone 정보 추가
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            except (ValueError, OverflowError, OSError) as e:
                self.logger.warning("published_parsed 파싱 실패", error=str(e))

        # 대안: published 문자열 직접 파싱 시도
        if hasattr(entry, 'published'):
            try:
                return datetime.fromisoformat(entry.published.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass

        return None

    def get_channel(self) -> Channel:
        """
        채널 반환

        Returns:
            Channel enum
        """
        return Channel.TRUTH_SOCIAL
