"""
Oracle Database 연결 관리

Trump Scan 프로젝트의 Oracle DB 연결을 관리합니다.
"""
from datetime import datetime, timezone, timedelta
import oracledb
from src.logger import get_logger
from src.models.raw_data import RawData
from src.models.channel import Channel
from config.database import DB_CONFIG


def _to_char_timestamp_tz(column_name: str) -> str:
    """TIMESTAMP WITH TIME ZONE 컬럼을 ISO 8601 형식 문자열로 변환하는 SQL 표현식"""
    return f"TO_CHAR({column_name}, 'YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM')"


def _parse_iso_timestamp(value: str) -> datetime:
    """ISO 8601 형식 문자열을 timezone-aware datetime으로 변환"""
    if value is None:
        return None
    return datetime.fromisoformat(value)


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

    def save_raw_data(self, raw_data: RawData) -> RawData:
        """
        원본 데이터 저장

        Args:
            raw_data: 저장할 RawData

        Returns:
            ID가 할당된 RawData
        """
        try:
            cursor = self.connection.cursor()

            # INSERT 쿼리 (RETURNING으로 생성된 ID 받기)
            insert_sql = """
                INSERT INTO raw_data (content, link, published_at, channel)
                VALUES (:content, :link, :published_at, :channel)
                RETURNING id INTO :id
            """

            # ID를 받을 변수 준비
            id_var = cursor.var(oracledb.NUMBER)

            # 실행
            cursor.execute(
                insert_sql,
                {
                    "content": raw_data.content,
                    "link": raw_data.link,
                    "published_at": raw_data.published_at,
                    "channel": raw_data.channel.value,  # Enum의 값 사용
                    "id": id_var
                }
            )

            # 생성된 ID를 RawData 객체에 할당
            generated_id = int(id_var.getvalue()[0])
            raw_data.id = generated_id

            # 커밋
            self.connection.commit()

            self.logger.debug("원본 데이터 저장 완료", id=raw_data.id, link=raw_data.link)

            cursor.close()
            return raw_data

        except oracledb.Error as e:
            self.connection.rollback()
            error_obj, = e.args
            self.logger.error(
                "데이터 저장 실패",
                error_code=error_obj.code if hasattr(error_obj, 'code') else None,
                error_message=str(error_obj.message) if hasattr(error_obj, 'message') else str(e),
                link=raw_data.link
            )
            raise
        except Exception as e:
            self.connection.rollback()
            self.logger.error(
                "데이터 저장 중 예외 발생",
                error=str(e),
                error_type=type(e).__name__,
                link=raw_data.link
            )
            raise

    def get_latest_raw_data(self) -> RawData:
        """
        가장 최근 raw_data 1건 조회

        Returns:
            RawData 또는 None (데이터 없는 경우)

        Note:
            published_at은 timezone-aware datetime으로 반환됩니다.
        """
        try:
            cursor = self.connection.cursor()

            # TO_CHAR로 타임존 포함 ISO 8601 형식으로 변환
            query = f"""
                SELECT
                    id,
                    content,
                    link,
                    {_to_char_timestamp_tz('published_at')} as published_at,
                    channel
                FROM raw_data
                ORDER BY published_at DESC
                FETCH FIRST 1 ROW ONLY
            """

            cursor.execute(query)
            row = cursor.fetchone()
            cursor.close()

            if row is None:
                return None

            db_id, content_lob, link, published_at_str, channel_value = row

            # CLOB -> str 변환
            content = content_lob.read() if hasattr(content_lob, 'read') else str(content_lob)

            # ISO 8601 문자열 -> timezone-aware datetime
            published_at = _parse_iso_timestamp(published_at_str)

            return RawData(
                id=int(db_id),
                content=content,
                link=link,
                published_at=published_at,
                channel=Channel(channel_value)
            )

        except oracledb.Error as e:
            error_obj, = e.args
            self.logger.error(
                "데이터 조회 실패",
                error_code=error_obj.code if hasattr(error_obj, 'code') else None,
                error_message=str(error_obj.message) if hasattr(error_obj, 'message') else str(e)
            )
            raise
