# ai/pipeline/analysis_input_builder.py

def stringify_grade_records(grade_records: dict) -> str:
    lines = []

    for year, semesters in grade_records.items():
        for semester, subjects in semesters.items():
            lines.append(f"[{year} {semester}]")
            for s in subjects:
                subject = s.get("과목")
                grade = s.get("석차등급") or s.get("등급")

                if subject and grade is not None:
                    lines.append(f"- {subject}: {grade}")

    return "\n".join(lines)


def build_analysis_inputs(parsed_result: dict) -> dict:
    # 🔥 1️⃣ 기본은 전부 전달
    ocr_data = dict(parsed_result)

    # 🔥 2️⃣ 성적은 LLM 친화 텍스트도 추가
    if "grade_records" in parsed_result:
        ocr_data["grade_text"] = stringify_grade_records(
            parsed_result["grade_records"]
        )

    return ocr_data
