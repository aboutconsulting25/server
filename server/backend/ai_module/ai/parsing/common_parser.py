from collections import defaultdict

def remove_last_table_each_page(result_json):
    cleaned = {"pages": []}

    for page in result_json.get("pages", []):
        tables = page.get("tables", [])
        if tables:
            tables = tables[:-1]  # 마지막 테이블 제거

        cleaned["pages"].append({
            "page_index": page["page_index"],
            "tables": tables
        })

    return cleaned


def merge_tables_by_title(result_json):
    merged = defaultdict(list)

    for page in result_json.get("pages", []):
        for table in page.get("tables", []):
            
            if table["table_title"] in [
                "봉사활동실적",
                "출결상황",
                "세부능력특기사항",
                "행동특성및종합의견"
            ]:
                continue
            
            if table["table_title"]:
                
                merged[table["table_title"]].append({
                    "page_index": page["page_index"],
                    "table_text": table["table_text"]
                })

    return dict(merged)
