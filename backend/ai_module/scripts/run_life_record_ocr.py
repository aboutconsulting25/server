import os
import json
from dotenv import load_dotenv

from ai.pipeline import run_full_pipeline


def main():
    load_dotenv()  

    pdf_path = "/Users/ham-in-a/Desktop/AboutConsulting/가천대_합격_생기부.pdf"

    ocr_api_url = os.getenv("OCR_API_URL")
    ocr_secret_key = os.getenv("OCR_SECRET_KEY")

    if not ocr_api_url or not ocr_secret_key:
        raise RuntimeError("OCR_API_URL 또는 OCR_SECRET_KEY가 설정되지 않았습니다.")

    result = run_full_pipeline(
        pdf_path=pdf_path,
        ocr_api_url=ocr_api_url,
        ocr_secret_key=ocr_secret_key,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
