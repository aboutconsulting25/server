"""
Celery tasks for document processing
"""
import os
import logging
from celery import shared_task
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_document_ocr(self, analysis_id):
    """
    생기부 문서 OCR 처리 및 파싱

    Args:
        analysis_id: DocumentAnalysis 모델의 ID (str)

    Returns:
        dict: 처리 결과
    """
    from apps.documents.models import DocumentAnalysis
    from ai_module.ai.pipeline import run_full_pipeline

    try:
        # DocumentAnalysis 조회
        analysis = DocumentAnalysis.objects.select_related('document').get(id=analysis_id)
        document = analysis.document

        logger.info(f"Starting OCR processing for document {document.id}")

        # 상태 업데이트
        analysis.status = 'PROCESSING'
        analysis.started_at = timezone.now()
        analysis.save()

        # 파일 경로 확인
        if not document.file:
            raise ValueError("문서 파일이 없습니다.")

        pdf_path = document.file.path

        # OCR API 설정 확인
        ocr_api_url = os.getenv("OCR_API_URL")
        ocr_secret_key = os.getenv("OCR_SECRET_KEY")

        if not ocr_api_url or not ocr_secret_key:
            raise ValueError("OCR API 설정이 없습니다. 환경 변수를 확인하세요.")

        logger.info(f"Running OCR pipeline for {pdf_path}")

        # AI 모듈 실행 (OCR + 파싱)
        result = run_full_pipeline(
            pdf_path=pdf_path,
            ocr_api_url=ocr_api_url,
            ocr_secret_key=ocr_secret_key
        )

        logger.info(f"OCR processing completed for document {document.id}")

        # 결과 저장
        analysis.ocr_result = result
        analysis.status = 'COMPLETED'
        analysis.completed_at = timezone.now()
        analysis.save()

        # Document 상태 업데이트
        document.status = 'COMPLETED'
        document.save()

        logger.info(f"Successfully processed document {document.id}")

        return {
            'success': True,
            'document_id': str(document.id),
            'analysis_id': str(analysis.id),
            'message': 'OCR 처리 완료'
        }

    except DocumentAnalysis.DoesNotExist:
        logger.error(f"DocumentAnalysis not found: {analysis_id}")
        return {
            'success': False,
            'error': 'DocumentAnalysis를 찾을 수 없습니다.'
        }

    except Exception as e:
        logger.error(f"Error processing document {analysis_id}: {str(e)}", exc_info=True)

        # 에러 상태 저장
        try:
            analysis = DocumentAnalysis.objects.get(id=analysis_id)
            analysis.status = 'FAILED'
            analysis.error_message = str(e)
            analysis.completed_at = timezone.now()
            analysis.save()

            document = analysis.document
            document.status = 'FAILED'
            document.save()
        except Exception as save_error:
            logger.error(f"Failed to save error state: {str(save_error)}")

        # Celery 재시도
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))

        return {
            'success': False,
            'error': str(e)
        }
