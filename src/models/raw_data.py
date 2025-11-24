"""
RawData: 수집된 원본 데이터 모델

모든 Collector가 반환하는 공통 데이터 구조를 정의합니다.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from src.models.channel import Channel


class RawData(BaseModel):
    """수집된 원본 데이터 모델"""

    model_config = ConfigDict(
        frozen=False,  # 필요시 불변으로 변경 가능
        str_strip_whitespace=True,  # 문자열 앞뒤 공백 자동 제거
    )

    id: Optional[int] = Field(None, description="DB 저장 후 생성된 ID")
    content: str = Field(..., description="포스트 내용")
    link: str = Field(..., description="포스트 링크")
    published_at: datetime = Field(..., description="발행 시간")
    channel: Channel = Field(..., description="수집 채널")

    def to_dict(self) -> dict:
        """딕셔너리로 변환 (직렬화용)"""
        return self.model_dump(mode='json')
