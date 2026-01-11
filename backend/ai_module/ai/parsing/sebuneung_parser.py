
import re


def extract_sebuneung_text_from_table(table):
    """
    세특 표에서 1행(header)을 제거하고 본문만 텍스트로 반환
    """
    texts = []

    for cell in table.get("cells", []):
        if cell.get("rowIndex") == 0:
            continue  # 🔥 헤더 제거

        for line in cell.get("cellTextLines", []):
            words = [w.get("inferText", "") for w in line.get("cellWords", [])]
            texts.append(" ".join(words))

    return " ".join(texts).strip()


def merge_all_sebuneung_text(tables_with_title):
    contents = []

    for page in tables_with_title["pages"]:
        for t in page["tables"]:
            if t["table_title"] == "세부능력특기사항":
                contents.append(
                    extract_sebuneung_text_from_table(t["raw_table"])
                )

    return " ".join(contents)

def normalize_subject(text):
    if not text:
        return text

    text = text.replace("Ⅱ", "II")
    text = text.replace("Ⅰ", "I")
    text = re.sub(r"\s+", "", text)  # 화학 II → 화학II
    return text


def split_sebuneung_by_subject(text, subject_list):
    """
    '과목명 :' 기준으로 세특 내용 분리
    """
    results = []

    subjects = sorted(subject_list, key=len, reverse=True)
    subjects_escaped = [re.escape(s) for s in subjects]
    subjects_escaped.append("자율적\\s*교육과정")

    subject_pattern = "|".join(subjects_escaped)

    pattern = re.compile(
        rf"(?P<subject>{subject_pattern})\s*[:：]\s*(?P<content>.*?)(?=(?:{subject_pattern})\s*[:：]|$)",
        re.DOTALL
    )

    for m in pattern.finditer(text):
        subject = m.group("subject")
        content = m.group("content").strip()

        if len(content) < 30:
            continue

        subject = normalize_subject(m.group("subject"))

        if subject.replace(" ", "") == "자율적교육과정":
            subject = "자율적 교육과정"

        results.append({
            "과목": subject,
            "내용": content
        })

    return results

def collect_subjects_from_grade_records(grade_records):
    subjects = set()

    for r in grade_records:
        name = r.get("과목")
        if name:
            subjects.add(name.strip())

    return sorted(subjects, key=len, reverse=True)



def extract_term(paragraph):
    m = re.search(r"\(([12]학기)\)", paragraph)
    return m.group(1) if m else None

def parse_sebuneung(tables_with_title, subject_list):
    merged_text = merge_all_sebuneung_text(tables_with_title)

    if not merged_text or "해당 사항 없음" in merged_text:
        return []
    
    merged_text = normalize_subject(merged_text)

    records = split_sebuneung_by_subject(merged_text, subject_list)
    
    return [
        {
            "과목": r["과목"],
            "내용": r["내용"]
        }
        for r in records
    ]
