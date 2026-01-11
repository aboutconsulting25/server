from ai.utils.table_utils import raw_table_to_matrix
from ai.utils.constants import (
    ATTENDANCE_KEYWORDS,
    COMMON_GRADE_HEADER,
    VOLUNTEER_TABLE_TITLE
)

def is_attendance_table(table):
    texts = []
    for cell in table.get("cells", []):
        for line in cell.get("cellTextLines", []):
            for w in line.get("cellWords", []):
                texts.append(w.get("inferText", ""))

    joined = " ".join(texts)
    hit = sum(k in joined for k in ATTENDANCE_KEYWORDS)

    return hit >= 2

def is_volunteer_table(table_title):
    return table_title == VOLUNTEER_TABLE_TITLE

def is_grade_table(raw_table):
    table = raw_table_to_matrix(raw_table)
    if not table:
        return False

    header = " ".join(table[0])
    return all(k in header for k in COMMON_GRADE_HEADER)

def is_sebuneung_table(table):
    """
    1행에 '과목' + '세부능력 및 특기사항' 이 동시에 존재하는지로 판별
    """
    first_row_texts = []

    for cell in table.get("cells", []):
        if cell.get("rowIndex") != 0:
            continue

        for line in cell.get("cellTextLines", []):
            for w in line.get("cellWords", []):
                first_row_texts.append(w.get("inferText", ""))

    header = "".join(first_row_texts).replace(" ", "")

    return "과목" in header and "세부능력및특기사항" in header

def is_overall_opinion_table(table):
    texts = []

    for cell in table.get("cells", []):
        for line in cell.get("cellTextLines", []):
            for w in line.get("cellWords", []):
                t = w.get("inferText", "").replace(" ", "")
                if t:
                    texts.append(t)

    joined = "".join(texts)

    return (
        "행동특성및종합의견" in joined
        or "행동특성종합의견" in joined
    )
