# Oracle Instant Client가 x64만 지원하므로 amd64 플랫폼 지정
FROM --platform=linux/amd64 python:3.13-slim

# Oracle Instant Client 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    libaio1t64 \
    wget \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Oracle Instant Client Basic Lite 21.15 설치
ENV ORACLE_INSTANT_CLIENT_VERSION=21.15.0.0.0
ENV ORACLE_HOME=/opt/oracle/instantclient_21_15
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_15
ENV TNS_ADMIN=/opt/oracle/wallet

RUN mkdir -p /opt/oracle && \
    cd /opt/oracle && \
    wget -q https://download.oracle.com/otn_software/linux/instantclient/2115000/instantclient-basiclite-linux.x64-${ORACLE_INSTANT_CLIENT_VERSION}dbru.zip && \
    unzip -q instantclient-basiclite-linux.x64-${ORACLE_INSTANT_CLIENT_VERSION}dbru.zip && \
    rm instantclient-basiclite-linux.x64-${ORACLE_INSTANT_CLIENT_VERSION}dbru.zip && \
    ln -sf /opt/oracle/instantclient_21_15/libclntsh.so.21.1 /opt/oracle/instantclient_21_15/libclntsh.so && \
    apt-get purge -y wget unzip && \
    apt-get autoremove -y && \
    apt-get clean

WORKDIR /app

# 의존성 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY main.py ./
COPY config/ ./config/
COPY src/ ./src/

# non-root 사용자 생성
RUN groupadd -r appgroup && useradd -r -g appgroup appuser && \
    chown -R appuser:appgroup /app

# Wallet 마운트 디렉토리 생성
RUN mkdir -p /opt/oracle/wallet && chown -R appuser:appgroup /opt/oracle/wallet

USER appuser

CMD ["python", "main.py"]
