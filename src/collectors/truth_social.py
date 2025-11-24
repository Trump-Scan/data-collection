"""
TruthSocialCollector: Truth Social RSS 피드 수집기

Trump's Truth Social 플랫폼에서 발언을 수집합니다.
"""
from typing import List, Optional
from datetime import datetime
import re
import httpx
import feedparser
from bs4 import BeautifulSoup
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

                # HTML 태그 제거 (한 번만 수행)
                raw_content = entry.get('summary', '')
                cleaned_content = self._clean_html(raw_content)

                # 정리된 content 유효성 검사
                if not self._is_valid_content(cleaned_content):
                    self.logger.debug("유효하지 않은 content", link=entry.get('link', ''))
                    continue

                # 데이터 구조화
                raw_data = RawData(
                    content=cleaned_content,
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
        soup = BeautifulSoup(html_content, 'html.parser')

        # 모든 텍스트 추출
        text = soup.get_text(separator=' ', strip=True)

        # 연속된 공백을 하나로
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def _is_valid_content(self, cleaned_content: str) -> bool:
        """
        정리된 content가 유효한지 검사 (비어있거나 의미없는 내용 제외)

        Args:
            cleaned_content: HTML이 이미 제거된 content 문자열

        Returns:
            유효하면 True, 아니면 False
        """
        if not cleaned_content or cleaned_content.strip() == "":
            return False

        # 텍스트가 너무 짧으면 제외
        if len(cleaned_content) < 10:
            return False

        # RT로 시작하는 리트윗 제외 (RT, RT:, RT @username 등)
        content_stripped = cleaned_content.strip()
        if content_stripped == "RT" or content_stripped.startswith("RT:") or content_stripped.startswith("RT @"):
            return False

        # URL만 있는 경우 제외 (http:// 또는 https://로 시작하는 경우)
        content_stripped = cleaned_content.strip()
        if content_stripped.startswith("http://") or content_stripped.startswith("https://"):
            return False

        return True

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
