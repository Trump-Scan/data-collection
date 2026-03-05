"""
Channel: 데이터 수집 채널 정의
"""
from enum import Enum


class Channel(str, Enum):
    """데이터 수집 채널"""

    TRUTH_SOCIAL = "truth_social"
    WHITE_HOUSE = "white_house"
    DUMMY = "dummy"
