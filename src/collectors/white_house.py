"""
WhiteHouseCollector: 백악관 뉴스 피드 수집기
"""

import re
from typing import List, Optional
from datetime import datetime
import httpx
import feedparser
from bs4 import BeautifulSoup
from src.collectors.base import BaseCollector
from src.models.channel import Channel
from src.models.raw_data import RawData


class WhiteHouseCollector(BaseCollector):
    """백악관 RSS 피드 수집 Collector"""

    RSS_FEED_URL = "https://www.whitehouse.gov/news/feed/"
    REQUEST_TIMEOUT = 30.0
    USER_AGENT = "Trump-Scan-Bot/1.0"

    def collect_raw_data(self, checkpoint: Optional[datetime]) -> List[RawData]:
        """
        백악관 RSS 피드에서 데이터 수집

        Args:
            checkpoint: 마지막으로 수집한 시간

        Returns:
            수집된 원본 데이터 리스트 (발행 시간 오름차순 정렬)
        """
        self.logger.info("백악관 데이터 수집 시작", checkpoint=checkpoint)

        try:
            # RSS 피드 호출
            headers = {"User-Agent": self.USER_AGENT}
            response = httpx.get(
                self.RSS_FEED_URL, headers=headers, timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            # RSS 파싱
            feed = feedparser.parse(response.text)

            collected_data = []

            for entry in feed.entries:
                # 발행 시간 파싱
                published_dt = self._parse_published_date(entry)

                if published_dt is None:
                    continue

                # checkpoint 이후 데이터만 수집
                if checkpoint and published_dt <= checkpoint:
                    continue

                # 본문 추출 및 정제
                # content:encoded 가 있으면 우선 사용, 없으면 summary 사용
                raw_content = ""
                if hasattr(entry, "content"):
                    raw_content = entry.content[0].value
                else:
                    raw_content = entry.get("summary", "")

                cleaned_content = self._clean_html(raw_content)

                # 데이터 구조화
                raw_data = RawData(
                    content=cleaned_content,
                    link=entry.get("link", ""),
                    published_at=published_dt,
                    channel=self.get_channel(),
                )

                collected_data.append(raw_data)

            # 발행 시간 기준 오름차순 정렬
            collected_data.sort(key=lambda x: x.published_at)

            self.logger.info("백악관 데이터 수집 완료", count=len(collected_data))
            return collected_data

        except httpx.HTTPError as e:
            self.logger.error("HTTP 요청 실패", error=str(e), url=self.RSS_FEED_URL)
            return []
        except Exception as e:
            self.logger.error(
                "데이터 수집 중 예외 발생", error=str(e), error_type=type(e).__name__
            )
            return []

    def _clean_html(self, html_content: str) -> str:
        """
        HTML 태그 제거 및 텍스트 추출

        Args:
            html_content: HTML이 포함된 문자열

        Returns:
            HTML 태그가 제거된 순수 텍스트
        """
        if not html_content:
            return ""

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(html_content, "html.parser")

        # 모든 텍스트 추출
        text = soup.get_text(separator=" ", strip=True)

        # 연속된 공백을 하나로
        text = re.sub(r"\s+", " ", text)

        return text.strip()

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
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                import time

                timestamp = time.mktime(entry.published_parsed)
                # UTC timezone 정보 추가
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            except (ValueError, OverflowError, OSError) as e:
                self.logger.warning("published_parsed 파싱 실패", error=str(e))

        # 대안: published 문자열 직접 파싱 시도
        if hasattr(entry, "published"):
            try:
                return datetime.fromisoformat(entry.published.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return None

    def get_channel(self) -> Channel:
        """
        채널 반환
        """
        return Channel.WHITE_HOUSE
