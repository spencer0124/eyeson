# 베이스 이미지: Python 3.8 기반 슬림 버전
FROM python:3.8-slim

# 작업 디렉토리 설정 (backend 내부)
WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean

# Conda 환경 설정 파일 복사 및 설치
COPY envs/conda.yml /tmp/conda.yml
RUN pip install --no-cache-dir conda \
    && conda env create -f /tmp/conda.yml -p /opt/conda/envs/eyeson \
    && conda clean --all \
    && rm -rf /tmp/conda.yml

# 백엔드 코드 복사
COPY . .

# Conda 환경 활성화 및 Uvicorn 실행
CMD ["/bin/bash", "-c", "source /opt/conda/etc/profile.d/conda.sh && conda activate eyeson && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]

# 포트 노출
EXPOSE 8000