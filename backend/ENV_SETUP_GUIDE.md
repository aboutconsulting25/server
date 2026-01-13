# 환경 변수 설정 가이드

## 🔐 문제 상황
- `.env` 파일은 Git에 올라가지 않음 (보안상 당연함)
- 서버에서 `git pull` 해도 환경 변수가 없음
- OCR API 키 같은 민감한 정보를 어떻게 관리할 것인가?

---

## ✅ **추천: 방법 1 - 서버에 .env 파일 직접 생성**

가장 간단하고 현재 구조에 맞는 방법입니다.

### 1. 서버에 SSH 접속
```bash
ssh user@13.53.39.217
cd /path/to/About-Consulting/server/backend
```

### 2. .env 파일 생성
```bash
# .env.example을 복사
cp .env.example .env

# vim으로 편집
vim .env
```

### 3. 실제 값 입력
```bash
# Django
DEBUG=0
SECRET_KEY=your-actual-secret-key
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=13.53.39.217,localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://postgres:aboutconsulting@about-consulting-db.cnswskaiyehs.eu-north-1.rds.amazonaws.com:5432/about_consulting?sslmode=require

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Naver OCR API (실제 키 입력)
OCR_API_URL=https://your-actual-naver-ocr-api-url
OCR_SECRET_KEY=your-actual-naver-ocr-secret-key

# AWS S3
USE_S3=False
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://13.53.39.217
```

### 4. 파일 권한 설정 (보안)
```bash
chmod 600 .env  # 소유자만 읽기/쓰기 가능
```

### 5. Docker Compose 재시작
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### ✅ 장점
- 가장 간단함
- 현재 docker-compose.prod.yml 구조와 완벽하게 호환
- 즉시 적용 가능

### ⚠️ 단점
- 서버마다 수동으로 설정해야 함
- 백업 필요 (서버 날아가면 키 날아감)

---

## 🔧 **방법 2 - GitHub Secrets + GitHub Actions**

CI/CD를 구축하고 자동 배포하는 방법입니다.

### 1. GitHub Secrets 등록

**GitHub 저장소 > Settings > Secrets and variables > Actions**

다음 Secrets 추가:
- `OCR_API_URL`
- `OCR_SECRET_KEY`
- `DATABASE_URL`
- `SECRET_KEY`
- `AWS_ACCESS_KEY_ID` (선택)
- `AWS_SECRET_ACCESS_KEY` (선택)

### 2. GitHub Actions Workflow 생성

`.github/workflows/deploy.yml` 파일 생성:

```yaml
name: Deploy to EC2

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to EC2
        uses: appleboy/ssh-action@master
        with:
          host: 13.53.39.217
          username: ${{ secrets.EC2_USERNAME }}
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd /path/to/server/backend
            git pull origin main

            # .env 파일 생성
            cat > .env << EOF
            DEBUG=0
            SECRET_KEY=${{ secrets.SECRET_KEY }}
            DATABASE_URL=${{ secrets.DATABASE_URL }}
            OCR_API_URL=${{ secrets.OCR_API_URL }}
            OCR_SECRET_KEY=${{ secrets.OCR_SECRET_KEY }}
            REDIS_URL=redis://redis:6379/0
            CELERY_BROKER_URL=redis://redis:6379/0
            CELERY_RESULT_BACKEND=redis://redis:6379/0
            EOF

            # Docker 재시작
            docker-compose -f docker-compose.prod.yml down
            docker-compose -f docker-compose.prod.yml build
            docker-compose -f docker-compose.prod.yml up -d
```

### ✅ 장점
- GitHub에서 중앙 관리
- 자동 배포
- Git push만 하면 서버 자동 업데이트

### ⚠️ 단점
- 초기 설정 복잡
- GitHub Actions 러닝 커브

---

## 🐳 **방법 3 - Docker Environment Variables**

`docker-compose.prod.yml`에서 환경 변수를 직접 정의하는 방법입니다.

### docker-compose.prod.yml 수정

```yaml
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DEBUG=0
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - OCR_API_URL=${OCR_API_URL}
      - OCR_SECRET_KEY=${OCR_SECRET_KEY}
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
```

그리고 서버에서 실행:
```bash
# 서버 쉘에서 환경 변수 export
export OCR_API_URL="https://..."
export OCR_SECRET_KEY="your-key"

# Docker Compose 실행
docker-compose -f docker-compose.prod.yml up -d
```

또는 별도의 `.env` 파일 사용하되 다른 이름으로:
```bash
# 서버에 .env.production 파일 생성
vim .env.production

# docker-compose.prod.yml에서
env_file:
  - .env.production  # Git에 올라가지 않는 파일
```

### ✅ 장점
- Docker 네이티브 방식
- 유연한 환경 관리

### ⚠️ 단점
- 여전히 서버에서 수동 설정 필요

---

## 🎯 **권장 사항**

### **현재 상황 (빠른 배포)**
→ **방법 1 (서버에 .env 직접 생성)** 사용

### **장기적 (프로덕션 환경)**
→ **방법 2 (GitHub Secrets + Actions)** 사용

---

## 📝 **실제 배포 단계 (방법 1)**

```bash
# 1. 로컬에서 Git push
git add .
git commit -m "Integrate AI OCR module"
git push origin main

# 2. 서버 SSH 접속
ssh user@13.53.39.217

# 3. 코드 pull
cd /path/to/About-Consulting/server/backend
git pull origin main

# 4. .env 파일 생성 (처음 한 번만)
cp .env.example .env
vim .env
# 실제 키 입력 후 저장

# 5. Docker 재빌드 및 재시작
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# 6. 로그 확인
docker-compose -f docker-compose.prod.yml logs -f web
```

---

## 🔒 **보안 주의사항**

### 서버에 .env 파일을 생성할 때:

1. **파일 권한 설정**
```bash
chmod 600 .env  # 소유자만 읽기/쓰기
```

2. **Git에 절대 커밋하지 않기**
```bash
# .gitignore 확인
cat .gitignore | grep .env
# 출력: .env
```

3. **.env 백업**
```bash
# 안전한 곳에 백업 (암호화된 스토리지)
cp .env .env.backup
# 로컬로 다운로드 (필요시)
scp user@13.53.39.217:/path/to/.env ./backup/.env
```

4. **정기적으로 키 교체**
- OCR API 키: 3개월마다
- SECRET_KEY: 6개월마다
- DB 비밀번호: 6개월마다

---

## ❓ FAQ

### Q: .env 파일이 서버에서 사라지면?
A: `.env.example`을 복사해서 다시 만들고 키 입력

### Q: OCR API 키는 어디서 받나요?
A: Naver Cloud Platform → AI NAVER API → OCR

### Q: 여러 서버에 배포하려면?
A: 각 서버마다 .env 파일 생성하거나 GitHub Actions 사용

### Q: .env 파일 변경 후 재시작 필요한가요?
A: 네, Docker Compose 재시작 필요:
```bash
docker-compose -f docker-compose.prod.yml restart
```

---

## 🚀 **지금 당장 해야 할 일**

```bash
# 1. 서버 접속
ssh user@13.53.39.217

# 2. 프로젝트 디렉토리로 이동
cd /path/to/About-Consulting/server/backend

# 3. .env 파일 생성
cp .env.example .env

# 4. vim으로 OCR API 키 입력
vim .env
# i 누르고 편집
# ESC 누르고 :wq로 저장

# 5. 확인
cat .env | grep OCR

# 6. Docker 재시작
docker-compose -f docker-compose.prod.yml restart
```

완료! 🎉
