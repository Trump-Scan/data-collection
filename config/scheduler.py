"""
스케줄러 설정
"""

SCHEDULER_CONFIG = {
    # 수집 작업 스케줄 설정
    "trigger": "interval",
    "minutes": 1,
    "id": "collect_job",
    "name": "데이터 수집 작업",

    # 추가 스케줄러 옵션 (필요 시 사용)
    # "misfire_grace_time": 60,  # 실행 시간을 놓쳤을 때 몇 초까지 실행할지
    # "coalesce": True,  # 여러 번 누락된 실행을 하나로 합칠지
    # "max_instances": 1,  # 동시 실행 가능한 작업 인스턴스 수
}
