"""
Redis 설정 템플릿

이 파일을 복사하여 config/redis.py로 만들고 실제 값으로 수정하세요.

사용법:
    cp config/redis.example.py config/redis.py
    # config/redis.py 파일을 편집하여 실제 값 입력
"""

# Redis 설정
REDIS_CONFIG = {
    # Redis 서버 호스트
    "host": "localhost",

    # Redis 서버 포트
    "port": 6379,

    # Redis 데이터베이스 번호 (0-15)
    "db": 0,

    # Redis 비밀번호 (필요한 경우만 설정)
    "password": "your_redis_password",
}
