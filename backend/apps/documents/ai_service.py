"""
AI Pipeline Service

Django <-> ai_module 브릿지.
PDF 파일을 받아 OCR → 파싱 → LLM 분석 파이프라인을 실행하고 결과를 반환한다.
"""

import sys
import os
import tempfile
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_AI_MODULE_LOADED = False


def _ensure_ai_module_path():
    """ai_module 디렉토리를 sys.path에 추가 (lazy, 한 번만 실행)"""
    global _AI_MODULE_LOADED
    if _AI_MODULE_LOADED:
        return

    # backend/ai_module/ → from ai.xxx import ... 가능하도록
    backend_dir = Path(__file__).resolve().parent.parent.parent  # backend/
    ai_module_dir = str(backend_dir / "ai_module")

    if ai_module_dir not in sys.path:
        sys.path.insert(0, ai_module_dir)
        logger.debug(f"Added ai_module to sys.path: {ai_module_dir}")

    _AI_MODULE_LOADED = True


def run_ai_pipeline(pdf_file, student_info: dict) -> dict:
    """
    생기부 PDF에 대해 전체 AI 파이프라인을 실행한다.

    OCR (Naver CLOVA) → 파싱 → LLM 분석 (OpenAI) 순서로 처리.

    Args:
        pdf_file: Django UploadedFile 객체
        student_info (dict): LLM 프롬프트에 필요한 학생 정보
            {
                "name": "홍길동",
                "grade": "3학년",
                "semester": "1학기",
                "targets": [
                    {"school": "서울대학교", "major": "컴퓨터공학부"},
                    ...
                ]
            }

    Returns:
        dict: 각 분석 타입의 결과 (save_key → raw_result)
            {
                "grade_strength_weakness": "...",
                "grade_in_depth_analysis": "...",
                "life_record_strength_weakness": "...",
                ...
            }

    Raises:
        EnvironmentError: Naver OCR / OpenAI 환경변수 미설정
        Exception: 파이프라인 실행 오류
    """
    _ensure_ai_module_path()

    from ai.pipeline.full_pipeline import run_full_pipeline  # noqa: PLC0415

    ocr_api_url = os.getenv("NAVER_OCR_API_URL")
    ocr_secret_key = os.getenv("NAVER_OCR_SECRET_KEY")

    if not ocr_api_url or not ocr_secret_key:
        raise EnvironmentError(
            "NAVER_OCR_API_URL 또는 NAVER_OCR_SECRET_KEY 환경변수가 설정되지 않았습니다. "
            ".env 파일을 확인하세요."
        )

    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError(
            "OPENAI_API_KEY 환경변수가 설정되지 않았습니다. "
            ".env 파일을 확인하세요."
        )

    tmp_dir = tempfile.mkdtemp(prefix="saenggibu_")
    logger.info(f"[AI Pipeline] 임시 디렉토리 생성: {tmp_dir}")

    try:
        # PDF → 임시 파일 저장
        pdf_path = os.path.join(tmp_dir, "input.pdf")
        with open(pdf_path, "wb") as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)

        # 페이지 이미지 출력 디렉토리 (임시 디렉토리 내부)
        pages_dir = os.path.join(tmp_dir, "pages")

        logger.info(f"[AI Pipeline] 학생: {student_info.get('name')} | 파이프라인 시작")

        results = run_full_pipeline(
            pdf_path=pdf_path,
            ocr_api_url=ocr_api_url,
            ocr_secret_key=ocr_secret_key,
            student_info=student_info,
            run_all=True,
            pages_dir=pages_dir,
        )

        logger.info(f"[AI Pipeline] 완료. 분석 항목: {list(results.keys())}")
        return results

    except Exception as e:
        logger.error(f"[AI Pipeline] 오류: {e}", exc_info=True)
        raise

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        logger.debug(f"[AI Pipeline] 임시 디렉토리 삭제: {tmp_dir}")
