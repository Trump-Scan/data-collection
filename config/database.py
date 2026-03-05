"""
데이터베이스 설정

모든 값은 환경변수로 오버라이드 가능합니다.
Docker 환경에서는 환경변수 또는 .env 파일로 실제 값을 주입하세요.
"""
import os

# Oracle Database 설정
DB_CONFIG = {
    "username": os.environ.get("DB_USERNAME", "YOUR_USERNAME"),
    "password": os.environ.get("DB_PASSWORD", "YOUR_PASSWORD"),
    "dsn": os.environ.get("DB_DSN", "YOUR_DSN"),
    "wallet_location": os.environ.get("DB_WALLET_LOCATION", "/path/to/wallet/directory"),
    "wallet_password": os.environ.get("DB_WALLET_PASSWORD", "YOUR_WALLET_PASSWORD"),
}
