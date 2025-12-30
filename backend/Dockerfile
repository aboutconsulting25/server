FROM python:3.11-slim

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements/base.txt requirements/production.txt requirements/
RUN pip install -r requirements/production.txt

# 애플리케이션 코드 복사
COPY . .

# 정적 파일 디렉토리 생성
RUN mkdir -p /app/staticfiles /app/media /app/logs

# 포트 노출
EXPOSE 8000

# 실행 명령
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
