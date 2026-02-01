# ai/analysis/analyzer.py

from ai.analysis.registry import PROMPT_REGISTRY
from ai.analysis.llm.prompt_loader import load_prompt
from ai.analysis.llm.openai_clients import run_llm


def run_analysis(
    *,
    prompt_name: str,
    student_info: dict,
    ocr_data: dict,
):
    if prompt_name not in PROMPT_REGISTRY:
        raise ValueError(f"Unknown prompt: {prompt_name}")

    task = PROMPT_REGISTRY[prompt_name]

    # =========================
    # 1️⃣ student_info 검증
    # =========================
    missing_student = [
        k for k in task.get("required_student_info", [])
        if k not in student_info or not student_info[k]
    ]
    if missing_student:
        raise ValueError(
            f"[{prompt_name}] Missing student_info: {missing_student}"
        )

    # =========================
    # 2️⃣ ocr_data 검증
    # =========================
    missing_ocr = [
        k for k in task.get("required_ocr", [])
        if k not in ocr_data or not ocr_data[k]
    ]
    if missing_ocr:
        raise ValueError(
            f"[{prompt_name}] Missing ocr_data: {missing_ocr}"
        )

    # =========================
    # 3️⃣ system prompt 로드
    # =========================
    system_prompt = load_prompt(task["prompt_file"])

    # =========================
    # 4️⃣ user prompt 생성
    # =========================
    user_prompt = task["input_builder"](student_info, ocr_data)

    # =========================
    # 5️⃣ LLM 실행
    # =========================
    result = run_llm(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    return {
        "prompt": prompt_name,
        "save_key": task["save_key"],
        "raw_result": result,
    }
