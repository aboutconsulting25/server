# ai/utils/text_utils.py

import re


def normalize_subject(text):
    if not text:
        return text

    text = text.replace("Ⅱ", "II")
    text = text.replace("Ⅰ", "I")
    text = re.sub(r"\s+", "", text)  # 화학 II → 화학II
    return text
