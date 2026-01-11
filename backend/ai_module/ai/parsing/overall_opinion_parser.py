def extract_overall_opinion_text_from_table(table):
    rows = {}

    for cell in table.get("cells", []):
        row = cell.get("rowIndex")
        col = cell.get("columnIndex")

        texts = []
        for line in cell.get("cellTextLines", []):
            for w in line.get("cellWords", []):
                t = w.get("inferText", "").strip()
                if t:
                    texts.append(t)

        if not texts:
            continue

        rows.setdefault(row, []).append((col, " ".join(texts)))

    sorted_rows = sorted(rows.items(), key=lambda x: x[0])

    contents = []

    for row_idx, cols in sorted_rows:
        cols = sorted(cols, key=lambda x: x[0])
        joined = " ".join(c[1] for c in cols)
        joined_nospace = joined.replace(" ", "")

        # ⛔ 헤더 제거
        if "행동특성및종합의견" in joined_nospace:
            continue
        if joined_nospace == "학년":
            continue

        contents.append(joined)

    return " ".join(contents).strip()


def merge_all_overall_opinion_text(tables_with_title):
    contents = []

    for page in tables_with_title["pages"]:
        for t in page["tables"]:
            if t["table_title"] == "행동특성및종합의견":
                contents.append(
                    extract_overall_opinion_text_from_table(t["raw_table"])
                )

    return " ".join(contents)

def parse_overall_opinion(tables_with_title):
    texts = []

    for page in tables_with_title["pages"]:
        for t in page["tables"]:
            if t["table_title"] == "행동특성및종합의견":
                table = t["raw_table"]
                text = extract_overall_opinion_text_from_table(table)
                if text:
                    texts.append(text)

    if not texts:
        return {}

    return {
        "내용": " ".join(texts)
    }
