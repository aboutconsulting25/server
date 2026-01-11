# ai/utils/table_utils.py

from collections import defaultdict


def raw_table_to_matrix(raw_table):
    rows = defaultdict(dict)

    for cell in raw_table.get("cells", []):
        r = cell["rowIndex"]
        c = cell["columnIndex"]

        texts = []
        for line in cell.get("cellTextLines", []):
            words = [w.get("inferText", "") for w in line.get("cellWords", [])]
            texts.append(" ".join(words))

        rows[r][c] = " ".join(texts).strip()

    matrix = []
    for r in sorted(rows.keys()):
        row = rows[r]
        max_c = max(row.keys())
        matrix.append([row.get(c, "") for c in range(max_c + 1)])

    return matrix
