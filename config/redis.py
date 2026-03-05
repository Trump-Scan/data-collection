"""
Redis 설정

모든 값은 환경변수로 오버라이드 가능합니다.
Docker 환경에서는 환경변수 또는 .env 파일로 실제 값을 주입하세요.
"""
import os

# Redis 설정
REDIS_CONFIG = {
    "host": os.environ.get("REDIS_HOST", "localhost"),
    "port": int(os.environ.get("REDIS_PORT", "6379")),
    "db": int(os.environ.get("REDIS_DB", "0")),
}
