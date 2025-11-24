"""
데이터베이스 설정 템플릿

이 파일을 복사하여 config/database.py로 만들고 실제 값으로 수정하세요.

사용법:
    cp config/database.example.py config/database.py
    # config/database.py 파일을 편집하여 실제 값 입력
"""

# Oracle Database 설정
DB_CONFIG = {
    # 데이터베이스 사용자 이름
    "username": "YOUR_USERNAME",

    # 데이터베이스 비밀번호
    "password": "YOUR_PASSWORD",

    # TNS 이름 또는 연결 문자열
    "dsn": "YOUR_DSN",

    # Oracle Wallet 파일 위치 (절대 경로)
    "wallet_location": "/path/to/wallet/directory",

    # Oracle Wallet 비밀번호
    "wallet_password": "YOUR_WALLET_PASSWORD",
}
