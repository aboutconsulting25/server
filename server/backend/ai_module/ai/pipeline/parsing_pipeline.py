# ai/pipeline/parsing_pipeline.py

from ai.ocr.table_detector import extract_tables_with_fixed_title

from ai.parsing.attendance_parser import extract_attendance_summary_from_ocr
from ai.parsing.volunteer_parser import extract_volunteer_summary_from_tables
from ai.parsing.grade_parser import (
    extract_grade_records_from_tables,
    build_nested_life_record_json
)
from ai.parsing.sebuneung_parser import parse_sebuneung
from ai.parsing.overall_opinion_parser import parse_overall_opinion
from ai.parsing.common_parser import (
    remove_last_table_each_page,
    merge_tables_by_title
)
from ai.parsing.sebuneung_parser import normalize_subject


def run_parsing_pipeline(ocr_result):
    # 출결
    attendance_summary = extract_attendance_summary_from_ocr(ocr_result)

    # 표 제목 분류
    tables_with_title = extract_tables_with_fixed_title(ocr_result)

    # 봉사
    volunteer_summary = extract_volunteer_summary_from_tables(tables_with_title)

    # 성적
    grade_records = extract_grade_records_from_tables(tables_with_title)
    nested_grade_json = build_nested_life_record_json(grade_records)

    # 과목 리스트 (세특 분리용)
    subject_list = sorted(
        {normalize_subject(r["과목"]) for r in grade_records if r.get("과목")},
        key=len,
        reverse=True
    )

    # 세특
    sebuneung_records = parse_sebuneung(
        tables_with_title,
        subject_list
    )

    # 행동특성
    overall_opinion = parse_overall_opinion(tables_with_title)

    # 기타 표
    cleaned = remove_last_table_each_page(tables_with_title)
    merged_tables = merge_tables_by_title(cleaned)

    return {
        "attendance_summary": attendance_summary,
        "volunteer_summary": volunteer_summary,
        "grade_records": nested_grade_json,
        "life_record_tables": merged_tables,
        "detail_ability": sebuneung_records,
        "overall_opinion": overall_opinion
    }
