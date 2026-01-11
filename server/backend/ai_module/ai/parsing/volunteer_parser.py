import re
from ai.utils.table_utils import raw_table_to_matrix

def extract_volunteer_hours_from_table(raw_table):
    table = raw_table_to_matrix(raw_table)

    # 1️⃣ '시간' 컬럼 위치 찾기
    time_col = None
    header_row = None

    for r, row in enumerate(table):
        for c, v in enumerate(row):
            if v.strip() == "시간":
                time_col = c
                header_row = r
                break
        if time_col is not None:
            break

    if time_col is None:
        return 0  # 시간 컬럼 없음

    # 2️⃣ 시간 컬럼 값만 합산
    total = 0
    for row in table[header_row + 1:]:
        if time_col >= len(row):
            continue

        cell = row[time_col]
        nums = re.findall(r"\d+", cell)
        if nums:
            total += int(nums[0])

    return total


def extract_volunteer_summary_from_tables(tables_with_title):
    """
    table_title == '봉사활동실적' 인 표에서
    봉사 시간 합계만 반환
    """
    total_hours = 0

    for page in tables_with_title.get("pages", []):
        for table in page.get("tables", []):

            if table.get("table_title") != "봉사활동실적":
                continue

            hours = extract_volunteer_hours_from_table(table["raw_table"])
            total_hours += hours

    return {"total_hours": total_hours}
