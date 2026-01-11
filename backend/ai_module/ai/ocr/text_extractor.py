

# ======================================================
# 표 제목 판별 로직 
# ======================================================
def extract_page_texts_with_position(image):
    texts = []

    for field in image.get("fields", []):
        text = field.get("inferText", "").strip()
        if not text:
            continue

        y = field["boundingPoly"]["vertices"][0]["y"]
        texts.append({"text": text, "y": y})

    return texts


def get_table_top_y(table):
    ys = []
    for cell in table.get("cells", []):
        for v in cell["boundingPoly"]["vertices"]:
            ys.append(v["y"])
    return min(ys) if ys else None

def extract_table_text(table):
    texts = []
    for cell in table.get("cells", []):
        for line in cell.get("cellTextLines", []):
            for w in line.get("cellWords", []):
                t = w.get("inferText", "").strip()
                if t:
                    texts.append(t)
    return " ".join(texts)
