"""
등급 변환 유틸리티

9등급제 ↔ 5등급제 상호 변환
"""

# 등급 변환 테이블 (상위 누적 비율 기준)
GRADE_9_PERCENTILES = {
    1: 0.04,
    2: 0.11,
    3: 0.23,
    4: 0.40,
    5: 0.60,
    6: 0.77,
    7: 0.89,
    8: 0.96,
    9: 1.00,
}

GRADE_5_PERCENTILES = {
    1: 0.10,
    2: 0.34,
    3: 0.66,
    4: 0.90,
    5: 1.00,
}


def convert_9_to_5(grade_9: float) -> float:
    """
    9등급제 → 5등급제 변환

    Args:
        grade_9: 9등급제 등급 (1.0 ~ 9.0)

    Returns:
        float: 5등급제 등급 (1.0 ~ 5.0)
    """
    if not (1.0 <= grade_9 <= 9.0):
        raise ValueError(f"Invalid grade_9: {grade_9}")

    percentile = get_percentile_from_grade_9(grade_9)
    grade_5 = get_grade_5_from_percentile(percentile)

    return round(grade_5, 2)


def convert_5_to_9(grade_5: float) -> float:
    """5등급제 → 9등급제 변환"""
    if not (1.0 <= grade_5 <= 5.0):
        raise ValueError(f"Invalid grade_5: {grade_5}")

    percentile = get_percentile_from_grade_5(grade_5)
    grade_9 = get_grade_9_from_percentile(percentile)

    return round(grade_9, 2)


def get_percentile_from_grade_9(grade_9: float) -> float:
    """9등급제 등급 → 상위 누적 비율 (선형 보간)"""
    if grade_9.is_integer():
        return GRADE_9_PERCENTILES[int(grade_9)]

    lower_grade = int(grade_9)
    upper_grade = lower_grade + 1

    lower_percentile = GRADE_9_PERCENTILES[lower_grade]
    upper_percentile = GRADE_9_PERCENTILES[upper_grade]

    ratio = grade_9 - lower_grade
    percentile = lower_percentile + (upper_percentile - lower_percentile) * ratio

    return percentile


def get_percentile_from_grade_5(grade_5: float) -> float:
    """5등급제 등급 → 상위 누적 비율"""
    if grade_5.is_integer():
        return GRADE_5_PERCENTILES[int(grade_5)]

    lower_grade = int(grade_5)
    upper_grade = lower_grade + 1

    lower_percentile = GRADE_5_PERCENTILES[lower_grade]
    upper_percentile = GRADE_5_PERCENTILES[upper_grade]

    ratio = grade_5 - lower_grade
    percentile = lower_percentile + (upper_percentile - lower_percentile) * ratio

    return percentile


def get_grade_9_from_percentile(percentile: float) -> float:
    """상위 누적 비율 → 9등급제 등급 (역 선형 보간)"""
    for grade, perc in GRADE_9_PERCENTILES.items():
        if abs(percentile - perc) < 0.0001:
            return float(grade)

    for grade in range(1, 9):
        lower_perc = GRADE_9_PERCENTILES[grade]
        upper_perc = GRADE_9_PERCENTILES[grade + 1]

        if lower_perc <= percentile <= upper_perc:
            ratio = (percentile - lower_perc) / (upper_perc - lower_perc)
            return grade + ratio

    if percentile < GRADE_9_PERCENTILES[1]:
        return 1.0
    return 9.0


def get_grade_5_from_percentile(percentile: float) -> float:
    """상위 누적 비율 → 5등급제 등급"""
    for grade, perc in GRADE_5_PERCENTILES.items():
        if abs(percentile - perc) < 0.0001:
            return float(grade)

    for grade in range(1, 5):
        lower_perc = GRADE_5_PERCENTILES[grade]
        upper_perc = GRADE_5_PERCENTILES[grade + 1]

        if lower_perc <= percentile <= upper_perc:
            ratio = (percentile - lower_perc) / (upper_perc - lower_perc)
            return grade + ratio

    if percentile < GRADE_5_PERCENTILES[1]:
        return 1.0
    return 5.0


def calculate_rank_from_grade(grade: float, total_students: int, grade_system: str = '9') -> int:
    """등급 → 등수 계산"""
    if grade_system == '9':
        percentile = get_percentile_from_grade_9(grade)
    else:
        percentile = get_percentile_from_grade_5(grade)

    rank = int(percentile * total_students)
    return max(1, rank)


def calculate_grade_from_rank(rank: int, total_students: int, grade_system: str = '9') -> float:
    """등수 → 등급 계산"""
    percentile = rank / total_students

    if grade_system == '9':
        grade = get_grade_9_from_percentile(percentile)
    else:
        grade = get_grade_5_from_percentile(percentile)

    return round(grade, 2)
