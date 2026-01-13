
from ai_module.ai.ocr.text_extractor import extract_page_texts_with_position, extract_table_text, get_table_top_y
from ai_module.ai.parsing.table_classifier import is_sebuneung_table, is_overall_opinion_table


TABLE_TITLE_CANDIDATES = [
    "출결상황",
    "창의적체험활동상황",
    "봉사활동실적"
]

def match_table_title(text):
    if not text:
        return ""
    for key in TABLE_TITLE_CANDIDATES:
        if key in text:
            return key
    return ""

def extract_tables_with_fixed_title(ocr_results):
    output = {"pages": []}

    for page_idx, image in enumerate(ocr_results.get("images", [])):
        page_texts = extract_page_texts_with_position(image)
        tables = image.get("tables", [])

        page_info = {
            "page_index": page_idx + 1,
            "tables": []
        }

        for idx, table in enumerate(tables):

            # ======================================================
            # 🔥 1️⃣ 세부능력특기사항 전용 탐지 (여기!!)
            # ======================================================
            if is_sebuneung_table(table):
                page_info["tables"].append({
                    "table_index": idx + 1,
                    "table_title": "세부능력특기사항",
                    "table_text": extract_table_text(table),
                    "raw_table": table
                })
                continue   
            # ======================================================
            # 🔥 1️⃣-2 행동특성종합의견 전용 탐지
            # ======================================================
            if is_overall_opinion_table(table):
                page_info["tables"].append({
                    "table_index": idx + 1,
                    "table_title": "행동특성및종합의견",
                    "table_text": extract_table_text(table),
                    "raw_table": table
                })
                continue   

            # ======================================================
            # 2️⃣ 일반 표 제목 탐지 로직
            # ======================================================    
            table_top_y = get_table_top_y(table)

            texts = []
            for cell in table.get("cells", []):
                for line in cell.get("cellTextLines", []):
                    for w in line.get("cellWords", []):
                        t = w.get("inferText", "").strip()
                        if t:
                            texts.append(t)

            table_text = " ".join(texts)

            table_title = determine_table_title(
                page_texts,
                table_top_y,
                table_text
            )

            page_info["tables"].append({
                "table_index": idx + 1,
                "table_title": table_title,
                "table_text": table_text,
                "raw_table": table
            })


        output["pages"].append(page_info)

    return output


def determine_table_title(page_texts, table_top_y, table_text):
    # 1️⃣ 표 위 텍스트
    candidates = [t for t in page_texts if t["y"] < table_top_y]
    candidates.sort(key=lambda x: table_top_y - x["y"])

    for c in candidates[:3]:
        title = match_table_title(c["text"])
        if title:
            return title

    # 2️⃣ 표 내부
    head_text = " ".join(table_text.split()[:30])
    title = match_table_title(head_text)
    if title:
        return title

    return ""
