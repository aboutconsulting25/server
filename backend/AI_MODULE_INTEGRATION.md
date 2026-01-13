# AI Module Integration Guide

## 🎯 통합 완료 사항

### 1. AI 모듈 Import 경로 수정 ✅
- 모든 `from ai.` → `from ai_module.ai.` 로 변경
- Django 프로젝트에서 정상적으로 import 가능

### 2. 환경 변수 추가 ✅
`.env` 파일에 추가됨:
```bash
# Naver OCR API
OCR_API_URL=https://your-naver-ocr-api-url
OCR_SECRET_KEY=your-naver-ocr-secret-key
```

**⚠️ 배포 전 필수**: 실제 Naver OCR API 키를 입력해야 합니다!

### 3. Dependencies 추가 ✅
`requirements/base.txt`에 추가됨:
```
pdf2image==1.16.3
pandas==2.1.4
numpy==1.26.2
requests==2.31.0
```

### 4. Celery Task 생성 ✅
`apps/documents/tasks.py` 생성:
- `process_document_ocr`: PDF → OCR → Parsing 비동기 처리
- 자동 재시도 기능 (최대 3회)
- 에러 핸들링 및 로깅

### 5. DocumentViewSet 연결 ✅
`apps/documents/views.py`:
- `start_analysis` 엔드포인트에서 Celery 태스크 호출
- 파일 업로드 후 자동으로 OCR 처리 시작

### 6. Dockerfile 업데이트 ✅
- `poppler-utils` 추가 (pdf2image 의존성)

---

## 🚀 배포 방법

### Step 1: 환경 변수 설정
```bash
# 서버의 .env 파일 수정
vi /path/to/server/backend/.env

# OCR API 키 입력
OCR_API_URL=https://your-actual-naver-ocr-url
OCR_SECRET_KEY=your-actual-secret-key
```

### Step 2: Docker 빌드 및 배포
```bash
cd /path/to/server/backend

# Docker 이미지 빌드
docker-compose -f docker-compose.prod.yml build

# 컨테이너 재시작
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f celery
```

### Step 3: Celery Worker 확인
```bash
# Celery worker가 실행 중인지 확인
docker-compose -f docker-compose.prod.yml ps

# Celery 로그 확인
docker-compose -f docker-compose.prod.yml logs celery
```

---

## 📡 API 사용 방법

### 1. 문서 업로드
```bash
POST /api/v1/documents/
Content-Type: multipart/form-data

{
  "student": "student-uuid",
  "document_type": "생기부",
  "title": "2024학년도 생활기록부",
  "file": <PDF file>
}
```

### 2. OCR 분석 시작
```bash
POST /api/v1/documents/{document_id}/analyze/

Response:
{
  "success": true,
  "message": "분석이 시작되었습니다.",
  "data": {
    "document_id": "...",
    "analysis_id": "...",
    "status": "PENDING"
  }
}
```

### 3. 분석 결과 조회
```bash
GET /api/v1/documents/{document_id}/latest-analysis/

Response:
{
  "success": true,
  "data": {
    "analysis_id": "...",
    "analysis_version": 1,
    "completed_at": "2024-01-13T12:00:00Z",
    "생기부_분석": {
      "attendance_summary": {...},
      "volunteer_summary": {...},
      "grade_records": {...},
      "detail_ability": {...},
      "overall_opinion": "..."
    }
  }
}
```

---

## 🔍 트러블슈팅

### 문제 1: OCR API 에러
```
Error: OCR API 설정이 없습니다.
```
**해결**: `.env` 파일에 `OCR_API_URL`, `OCR_SECRET_KEY` 확인

### 문제 2: pdf2image 에러
```
Error: pdftoppm not found
```
**해결**: Docker 이미지 재빌드 (poppler-utils 설치됨)

### 문제 3: Celery task 실행 안됨
```bash
# Celery worker 상태 확인
docker-compose -f docker-compose.prod.yml logs celery

# Redis 연결 확인
docker-compose -f docker-compose.prod.yml exec web python -c "import redis; r = redis.from_url('redis://redis:6379/0'); print(r.ping())"
```

### 문제 4: Import 에러
```
ModuleNotFoundError: No module named 'ai'
```
**해결**: 모든 import가 `ai_module.ai.`로 수정되었는지 확인

---

## 📊 처리 플로우

```
1. 프론트엔드: PDF 업로드
   ↓
2. DocumentViewSet: Document 생성
   ↓
3. start_analysis 호출
   ↓
4. DocumentAnalysis 생성 (status='PENDING')
   ↓
5. Celery Task 큐에 추가
   ↓
6. Celery Worker: process_document_ocr 실행
   ↓
7. AI Module: run_full_pipeline
   ├─ pdf_to_images (PDF → 이미지)
   ├─ process_multiple_images (Naver OCR)
   └─ run_parsing_pipeline (파싱)
   ↓
8. DocumentAnalysis 업데이트 (status='COMPLETED')
   ↓
9. 프론트엔드: latest-analysis API로 결과 조회
```

---

## 🔐 보안 주의사항

1. **OCR API 키 보호**
   - `.env` 파일을 git에 커밋하지 마세요
   - 서버에서만 실제 키 사용

2. **파일 업로드 검증**
   - PDF 파일만 업로드 허용
   - 파일 크기 제한 설정 권장

3. **에러 메시지**
   - 프로덕션에서는 상세 에러 메시지 노출 주의

---

## 📈 모니터링

### Celery Task 모니터링
```bash
# Flower (Celery 모니터링 도구) 접속
http://your-server:5555
```

### 로그 위치
```bash
# Django 로그
docker-compose -f docker-compose.prod.yml logs web

# Celery 로그
docker-compose -f docker-compose.prod.yml logs celery
```

---

## 🎉 테스트

### 1. 로컬 테스트 (Docker 없이)
```bash
cd backend

# 환경 변수 설정
export OCR_API_URL="your-url"
export OCR_SECRET_KEY="your-key"

# Python 경로 설정
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 직접 실행
python ai_module/scripts/run_life_record_ocr.py
```

### 2. 서버 테스트
```bash
# API 테스트
curl -X POST http://your-server/api/v1/documents/{id}/analyze/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 결과 확인
curl http://your-server/api/v1/documents/{id}/latest-analysis/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 향후 작업

- [ ] OpenAI API 연동 (생기부 분석)
- [ ] S3 파일 저장 활성화
- [ ] 에러 알림 설정 (Sentry)
- [ ] 성능 모니터링
- [ ] 단위 테스트 작성
