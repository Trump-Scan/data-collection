"""
MessageQueue publish 테스트 - DB에서 최근 raw_data 조회 후 발행
"""
from time import sleep

import pytest
from datetime import datetime
from src.infrastructure.database import Database
from src.infrastructure.message_queue import MessageQueue


class TestMessageQueuePublish:
    """DB 조회 후 MessageQueue publish 테스트"""

    @pytest.fixture
    def database(self):
        """Database 인스턴스 생성"""
        return Database()

    @pytest.fixture
    def message_queue(self):
        """MessageQueue 인스턴스 생성"""
        return MessageQueue()

    def test_publish_latest_raw_data_from_db(self, database, message_queue):
        """
        DB에서 최근 raw_data 1건 조회 후 MessageQueue에 publish

        - published_at에 타임존 정보가 포함되어 있는지 확인
        - publish 성공 여부 확인
        """
        # 1. DB에서 최근 raw_data 1건 조회
        raw_data = database.get_latest_raw_data(625)

        # 데이터가 없으면 테스트 스킵
        if raw_data is None:
            pytest.skip("DB에 raw_data가 없습니다")

        print(f"\n=== DB에서 조회된 데이터 ===")
        print(f"ID: {raw_data.id}")
        content = raw_data.content
        print(f"Content: {content[:50]}..." if len(content) > 50 else f"Content: {content}")
        print(f"Link: {raw_data.link}")
        print(f"Published At: {raw_data.published_at}")
        print(f"Published At Timezone: {raw_data.published_at.tzinfo}")
        print(f"Channel: {raw_data.channel.value}")

        # 2. 타임존 정보 확인
        assert isinstance(raw_data.published_at, datetime), "published_at은 datetime이어야 합니다"
        assert raw_data.published_at.tzinfo is not None, "published_at에 타임존 정보가 있어야 합니다"
        print(f"\n[OK] published_at에 타임존 정보 있음: {raw_data.published_at.tzinfo}")

        # 3. to_dict() 직렬화 확인
        data_dict = raw_data.to_dict()
        print(f"\n=== 직렬화된 데이터 (to_dict) ===")
        print(f"published_at in dict: {data_dict['published_at']}")

        # 4. MessageQueue에 publish
        message_id = message_queue.publish(raw_data)

        print(f"\n=== Publish 결과 ===")
        print(f"Message ID: {message_id}")

        # 5. 검증
        assert message_id is not None
        assert isinstance(message_id, str)
        print("\n[SUCCESS] MessageQueue publish 성공!")

    def test_publish_multiple_raw_data_from_db(self, database, message_queue):
        """
        DB에서 여러 raw_data 조회 후 MessageQueue에 publish

        - 여러 ID에 대해 순차적으로 처리
        - 각각의 publish 성공 여부 확인
        """
        # 테스트할 raw_data ID 목록
        raw_data_ids = [1,2,3]

        print(f"\n=== 테스트할 ID 목록: {raw_data_ids} ===")

        success_count = 0
        fail_count = 0

        for raw_data_id in raw_data_ids:
            sleep(10)
            print(f"\n--- Processing ID: {raw_data_id} ---")

            # 1. DB에서 raw_data 조회
            raw_data = database.get_latest_raw_data(raw_data_id)

            if raw_data is None:
                print(f"[SKIP] ID {raw_data_id}: 데이터 없음")
                fail_count += 1
                continue

            print(f"ID: {raw_data.id}")
            content = raw_data.content
            print(f"Content: {content[:50]}..." if len(content) > 50 else f"Content: {content}")
            print(f"Published At: {raw_data.published_at}")

            # 2. 타임존 정보 확인
            assert raw_data.published_at.tzinfo is not None, f"ID {raw_data_id}: 타임존 정보 없음"

            # 3. MessageQueue에 publish
            message_id = message_queue.publish(raw_data)

            assert message_id is not None
            print(f"[OK] Message ID: {message_id}")
            success_count += 1

        print(f"\n=== 결과 요약 ===")
        print(f"성공: {success_count}, 실패/스킵: {fail_count}")

        # 최소 1건은 성공해야 함
        assert success_count > 0, "최소 1건 이상 publish 성공해야 합니다"
        print("\n[SUCCESS] 다중 publish 테스트 완료!")
