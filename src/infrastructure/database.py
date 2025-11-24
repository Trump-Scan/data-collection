"""
Oracle Database 연결 관리

Trump Scan 프로젝트의 Oracle DB 연결을 관리합니다.
"""
import oracledb
from src.logger import get_logger
from config.database import DB_CONFIG


class Database:
    """Oracle Database 연결 관리 클래스"""

    def __init__(self):
        """Database 초기화 및 연결"""
        self.logger = get_logger(__name__)

        # DB 설정 로드
        username = DB_CONFIG["username"]
        password = DB_CONFIG["password"]
        dsn = DB_CONFIG["dsn"]
        wallet_location = DB_CONFIG["wallet_location"]
        wallet_password = DB_CONFIG["wallet_password"]

        # 연결 생성
        try:
            self.logger.info("Connecting to Oracle database...", dsn=dsn)

            self.connection = oracledb.connect(
                user=username,
                password=password,
                dsn=dsn,
                config_dir=wallet_location,
                wallet_location=wallet_location,
                wallet_password=wallet_password
            )

            self.logger.info("Database connection successful", dsn=dsn)

        except oracledb.Error as e:
            error_obj, = e.args
            self.logger.error(
                "Failed to connect to database",
                error_code=error_obj.code if hasattr(error_obj, 'code') else None,
                error_message=str(error_obj.message) if hasattr(error_obj, 'message') else str(e)
            )
            raise
        except Exception as e:
            self.logger.error(
                "Unexpected error during database connection",
                error=str(e),
                error_type=type(e).__name__
            )
            raise
