## ai/pipeline/analysis_pipeline.py

from ai.analysis.analyzer import run_analysis
from ai.analysis.registry import PROMPT_REGISTRY


def run_analysis_from_inputs(
    *,
    student_info: dict,
    ocr_data: dict,
    run_all: bool = True,
    prompt_names: list[str] | None = None,
):


    # ==================================================
    # 0️⃣ 기본 방어
    # ==================================================
    if not ocr_data:
        raise ValueError("ocr_data is empty. Analysis cannot proceed.")

    print("🧪 OCR DATA KEYS:", list(ocr_data.keys()))

    # ==================================================
    # 1️⃣ 실행할 프롬프트 결정
    # ==================================================
    if run_all:
        prompt_names = list(PROMPT_REGISTRY.keys())
    else:
        if not prompt_names:
            raise ValueError("prompt_names must be provided when run_all=False")

    results = {}

    # ==================================================
    # 2️⃣ 프롬프트별 분석 실행
    # ==================================================
    for prompt_name in prompt_names:
        if prompt_name not in PROMPT_REGISTRY:
            raise ValueError(f"Unknown prompt_name: {prompt_name}")

        prompt_meta = PROMPT_REGISTRY[prompt_name]

        
        required_keys = prompt_meta.get("required_keys", [])
        missing_keys = [k for k in required_keys if k not in ocr_data]

        if missing_keys:
            raise ValueError(
                f"[{prompt_name}] missing required ocr_data keys: {missing_keys}"
            )

        
        

        # ----------------------------------------------
        # LLM 실행
        # ----------------------------------------------
        output = run_analysis(
            prompt_name=prompt_name,
            student_info=student_info,
            ocr_data=ocr_data,
        )

        # ----------------------------------------------
        # 결과 저장
        # ----------------------------------------------
        save_key = output.get("save_key")
        raw_result = output.get("raw_result")

        if not save_key:
            raise ValueError(
                f"[{prompt_name}] output missing 'save_key'"
            )

        results[save_key] = raw_result


    return results
