# ai/pipeline/full_pipeline.py

from ai.pipeline.ocr_pipeline import run_ocr_pipeline
from ai.pipeline.parsing_pipeline import run_parsing_pipeline
from ai.pipeline.analysis_input_builder import build_analysis_inputs
from ai.pipeline.analysis_pipeline import run_analysis_from_inputs


def run_full_pipeline(
    *,
    pdf_path: str,
    ocr_api_url: str,
    ocr_secret_key: str,
    student_info: dict,
    run_all: bool = True,
    prompt_names: list[str] | None = None,
    pages_dir: str | None = None,
):
    ocr_result = run_ocr_pipeline(
        pdf_path=pdf_path,
        ocr_api_url=ocr_api_url,
        ocr_secret_key=ocr_secret_key,
        pages_dir=pages_dir,
    )

    parsed_result = run_parsing_pipeline(ocr_result)

    ocr_data = build_analysis_inputs(parsed_result)
    
    return run_analysis_from_inputs(
        student_info=student_info,
        ocr_data=ocr_data,
        run_all=run_all,
        prompt_names=prompt_names,
    )
