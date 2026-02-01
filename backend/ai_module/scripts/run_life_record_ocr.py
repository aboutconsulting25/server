# ai/module/scripts/run_life_record_ocr.py

import os
import json
from pathlib import Path
from dotenv import load_dotenv


from ai.pipeline import run_full_pipeline


def main():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)

    pdf_path = "/Users/ham-in-a/Desktop/sample_life_record.pdf"


    ocr_api_url = os.getenv("OCR_API_URL")
    ocr_secret_key = os.getenv("OCR_SECRET_KEY")

    if not ocr_api_url or not ocr_secret_key:
        raise RuntimeError("OCR_API_URL 또는 OCR_SECRET_KEY가 설정되지 않았습니다.")

    # ==========================
    # 👤 테스트용으로 학생 정보 넣어두었습니다. 
    # 'student_info'가 있다고 가정한 파이프라인 구조로 되어있습니다. 
    # ==========================
    student_info = {
        "name": "김형섭",
        "grade": "고등학교 3학년",
        "semester": "2학기",
        "targets": [
            {"school": "가천대학교", "major": "소프트웨어융합학과"},
            {"school": "한양대학교", "major": "컴퓨터소프트웨어학부"},
        ],
    }


    result = run_full_pipeline(
        pdf_path=pdf_path,
        ocr_api_url=ocr_api_url,
        ocr_secret_key=ocr_secret_key,
        student_info=student_info,  
        run_all=True
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
