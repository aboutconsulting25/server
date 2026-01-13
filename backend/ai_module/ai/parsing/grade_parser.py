import re
from collections import defaultdict

from ai_module.ai.parsing.table_classifier import is_grade_table
from ai_module.ai.utils.table_utils import raw_table_to_matrix


def classify_grade_table(raw_table):
    table = raw_table_to_matrix(raw_table)
    header = " ".join(table[0])

    if "석차" in header:
        return "교과학습발달상황"
    if "분포" in header:
        return "진로 선택 과목"
    return "체육·예술"

def clean_achievement(text):
    if not text:
        return None
    m = re.match(r"([A-Z])", text.strip())
    return m.group(1) if m else None

def clean_merged_sum_row(교과, 단위_raw):
    교과 = 교과.replace("이수단위 합계", "").strip()
    nums = re.findall(r"\d+", 단위_raw)
    단위수 = int(nums[0]) if nums else None
    return 교과, 단위수

def extract_grade_records_from_tables(tables_with_title):
    results = []

    current_grade = 1
    current_term = 0  # 국어 등장 기준

    for page in tables_with_title["pages"]:
        for t in page["tables"]:
            raw_table = t["raw_table"]

            if not is_grade_table(raw_table):
                continue

            table_type = classify_grade_table(raw_table)
            table = raw_table_to_matrix(raw_table)

            for row in table[1:]:
                if len(row) < 4:
                    continue

                교과 = row[1].strip()
                과목 = row[2].strip()
                단위_raw = row[3].strip()

                if not 과목:
                    continue

                # 🔥 학년/학기 전환 (교과 == 국어 기준)
                if table_type == "교과학습발달상황" and 교과 == "국어":
                    current_term += 1
                    if current_term == 3:
                        current_term = 1
                        current_grade += 1

                # 단위수 처리 (합계 섞임 대응)
                if "합계" in 교과:
                    교과, 단위수 = clean_merged_sum_row(교과, 단위_raw)
                else:
                    nums = re.findall(r"\d+", 단위_raw)
                    if not nums:
                        continue
                    단위수 = int(nums[0])

                record = {
                    "구분": table_type,
                    "교과": 교과,
                    "과목": 과목,
                    "단위수": 단위수
                }

                # 교과 성적표만 학년/학기 포함
                if table_type == "교과학습발달상황":
                    record["학년"] = current_grade
                    record["학기"] = current_term
                    석차 = row[-1].strip()
                    record["석차등급"] = int(석차) if 석차.isdigit() else None

                else:
                    raw_val = row[5].strip() if len(row) > 5 else row[4].strip()
                    record["성취도"] = clean_achievement(raw_val)

                results.append(record)

    return results

def build_nested_life_record_json(records):
    result = defaultdict(lambda: {
        "1학기": [],
        "2학기": [],
        "진로선택과목": [],
        "체육·예술": []
    })

    current_grade = None

    for r in records:
        if "학년" in r:
            current_grade = r["학년"]

        if current_grade is None:
            continue

        grade_key = f"{current_grade}학년"

        if r["구분"] == "교과학습발달상황":
            term_key = f"{r['학기']}학기"
            result[grade_key][term_key].append({
                "교과": r["교과"],
                "과목": r["과목"],
                "단위수": r["단위수"],
                "석차등급": r["석차등급"]
            })

        elif r["구분"] == "진로 선택 과목":
            result[grade_key]["진로선택과목"].append({
                "교과": r["교과"],
                "과목": r["과목"],
                "단위수": r["단위수"],
                "성취도": r["성취도"]
            })

        elif r["구분"] == "체육·예술":
            result[grade_key]["체육·예술"].append({
                "교과": r["교과"],
                "과목": r["과목"],
                "단위수": r["단위수"],
                "성취도": r["성취도"]
            })

    return dict(result)
