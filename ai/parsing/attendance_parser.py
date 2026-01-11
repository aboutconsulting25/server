import pandas as pd
from ai.parsing.table_classifier import is_attendance_table


def make_attendance_summary_json(numeric_df):
    summary = {}
    for col in numeric_df.columns:
        if col in ["학년", "수업일수", "특기사항"]:
            continue
        summary[col] = int(numeric_df[col].sum())
    return summary


def extract_attendance_summary_from_ocr(ocr_result):
    """
    OCR 원본에서 출결표 자동 탐색 → 요약 JSON 반환
    """
    for image in ocr_result.get("images", []):
        tables = image.get("tables", [])
        for table in tables:
            if not is_attendance_table(table):
                continue

            # 셀 파싱
            data = []
            for cell in table["cells"]:
                row = cell.get("rowIndex")
                col = cell.get("columnIndex")
                texts = []
                for line in cell.get("cellTextLines", []):
                    words = [w.get("inferText", "") for w in line.get("cellWords", [])]
                    texts.append(" ".join(words))
                text = " ".join(texts).strip()
                data.append((row, col, text))

            df = pd.DataFrame(data, columns=["row", "col", "text"])
            pivot = df.pivot(index="row", columns="col", values="text").fillna("")
            pivot.reset_index(drop=True, inplace=True)

            # 헤더 병합
            header1 = pivot.iloc[0].tolist()
            header2 = pivot.iloc[1].tolist()

            last = ""
            for i in range(len(header1)):
                if header1[i] == "":
                    header1[i] = last
                else:
                    last = header1[i]

            headers = []
            for h1, h2 in zip(header1, header2):
                headers.append(f"{h1}_{h2}" if h1 and h2 else h1 or h2)

            data_df = pivot.iloc[2:].copy()
            data_df.columns = headers
            data_df.reset_index(drop=True, inplace=True)

            def to_int(x):
                try:
                    return int(str(x).strip())
                except:
                    return 0

            numeric_df = data_df.applymap(to_int)
            return make_attendance_summary_json(numeric_df)

    return {}  # 출결표 없음
