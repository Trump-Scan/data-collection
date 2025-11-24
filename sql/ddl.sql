CREATE TABLE raw_data (
    -- 기본 키
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- 데이터 필드
    content CLOB NOT NULL,              -- 포스트 내용 (긴 텍스트)
    link VARCHAR2(2000) NOT NULL,       -- 포스트 링크
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,    -- 발행 시간 (원본 게시 시간)
    channel VARCHAR2(50) NOT NULL,      -- 수집 채널 (TRUTH_SOCIAL, NEWS 등)

    -- 메타 데이터
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL  -- 생성 시간 (시스템 기록)
);

-- 인덱스 생성
CREATE INDEX idx_raw_data_published_at ON raw_data(published_at);
CREATE INDEX idx_raw_data_channel ON raw_data(channel);
CREATE INDEX idx_raw_data_created_at ON raw_data(created_at);

-- 테이블 코멘트
COMMENT ON TABLE raw_data IS '트럼프 대통령 발언 원본 데이터';
COMMENT ON COLUMN raw_data.id IS '원본 데이터 고유 ID (자동 생성)';
COMMENT ON COLUMN raw_data.content IS '포스트 내용 (전체 텍스트)';
COMMENT ON COLUMN raw_data.link IS '포스트 원본 링크 URL';
COMMENT ON COLUMN raw_data.published_at IS '원본 게시 시간';
COMMENT ON COLUMN raw_data.channel IS '수집 채널';
COMMENT ON COLUMN raw_data.created_at IS '데이터 생성 시간 (시스템 기록)';