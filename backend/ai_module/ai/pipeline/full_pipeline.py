# ai/pipeline/full_pipeline.py

from ai_module.ai.pipeline.ocr_pipeline import run_ocr_pipeline
from ai_module.ai.pipeline.parsing_pipeline import run_parsing_pipeline


def run_full_pipeline(
    pdf_path,
    ocr_api_url,
    ocr_secret_key,
):
    ocr_result = run_ocr_pipeline(
        pdf_path=pdf_path,
        ocr_api_url=ocr_api_url,
        ocr_secret_key=ocr_secret_key,
    )

    parsed_result = run_parsing_pipeline(ocr_result)
    return parsed_result
