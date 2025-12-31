"""
대학별 특수 등급 변환 로직

각 대학의 고유한 등급 변환 규칙을 구현
"""

from typing import Dict, List, Optional
from decimal import Decimal


# ==================== 가천대 변환 ====================

class GachonConverter:
    """가천대 등급 변환기"""

    # 학년별 반영비율
    GRADE_WEIGHTS = {
        1: 0.0,    # 1학년: 0%
        2: 1.0,    # 2학년: 100%
        3: 1.0,    # 3학년 1학기: 100%
    }

    # 인문계열 변환등급 (석차등급 → 변환등급)
    HUMANITIES_GRADE_MAP = {
        1: 'A', 2: 'A',
        3: 'B', 4: 'B',
        5: 'C', 6: 'C',
        7: 'D', 8: 'D',
        9: 'E',
    }

    # 자연계열 변환등급 → 배점
    SCIENCE_SCORE_MAP = {
        'A': 100,
        'B': 99.5,
        'C': 99,
        'D': 90,
        'E': 70,
    }

    # 자연계열 석차등급 → 변환등급
    SCIENCE_GRADE_MAP = {
        1: 'A',
        2: 'B', 3: 'B',
        4: 'C', 5: 'C',
        6: 'D', 7: 'D',
        8: 'E', 9: 'E',
    }

    # 의예과/한의예과/약학과 석차등급 → 배점
    MEDICAL_SCORE_MAP = {
        1: 100,
        2: 99.5,
        3: 99,
        4: 98.5,
        5: 98,
        6: 97.5,
        7: 85,
        8: 60,
        9: 30,
    }

    @classmethod
    def convert_humanities(cls, grade: int) -> str:
        """
        인문계열 석차등급 → 변환등급

        Args:
            grade: 석차등급 (1-9)

        Returns:
            str: 변환등급 (A-E)

        Examples:
            >>> GachonConverter.convert_humanities(1)
            'A'
            >>> GachonConverter.convert_humanities(3)
            'B'
        """
        if not (1 <= grade <= 9):
            raise ValueError(f"Invalid grade: {grade}. Must be 1-9")

        return cls.HUMANITIES_GRADE_MAP[grade]

    @classmethod
    def convert_science(cls, grade: int) -> Dict[str, any]:
        """
        자연계열 석차등급 → 변환등급 + 배점

        Args:
            grade: 석차등급 (1-9)

        Returns:
            dict: {'converted_grade': 'A', 'score': 100}

        Examples:
            >>> GachonConverter.convert_science(1)
            {'converted_grade': 'A', 'score': 100}
            >>> GachonConverter.convert_science(3)
            {'converted_grade': 'B', 'score': 99.5}
        """
        if not (1 <= grade <= 9):
            raise ValueError(f"Invalid grade: {grade}")

        converted_grade = cls.SCIENCE_GRADE_MAP[grade]
        score = cls.SCIENCE_SCORE_MAP[converted_grade]

        return {
            'converted_grade': converted_grade,
            'score': score
        }

    @classmethod
    def convert_medical(cls, grade: int) -> float:
        """
        의예과/한의예과/약학과 석차등급 → 배점

        Args:
            grade: 석차등급 (1-9)

        Returns:
            float: 배점

        Examples:
            >>> GachonConverter.convert_medical(1)
            100
            >>> GachonConverter.convert_medical(5)
            98
        """
        if not (1 <= grade <= 9):
            raise ValueError(f"Invalid grade: {grade}")

        return cls.MEDICAL_SCORE_MAP[grade]

    @classmethod
    def calculate_gpa(
        cls,
        grades: List[Dict],
        major_type: str = 'humanities'
    ) -> float:
        """
        가천대 방식으로 평균 계산

        Args:
            grades: 과목별 성적 리스트
                [
                    {'grade': 2, 'credit': 3, 'year': 2},
                    {'grade': 3, 'credit': 4, 'year': 2},
                    ...
                ]
            major_type: 'humanities', 'science', 'medical'

        Returns:
            float: 환산 평균

        Examples:
            >>> grades = [
            ...     {'grade': 2, 'credit': 3, 'year': 2},
            ...     {'grade': 3, 'credit': 4, 'year': 2},
            ... ]
            >>> GachonConverter.calculate_gpa(grades, 'science')
            99.64  # (99.5*3 + 99*4) / 7
        """
        total_score = 0
        total_credit = 0

        for item in grades:
            grade = item['grade']
            credit = item['credit']
            year = item['year']

            # 1학년은 반영 안 함
            if year == 1:
                continue

            # 전형별 점수 계산
            if major_type == 'humanities':
                # 인문계열은 변환등급만 (배점 없음)
                converted = cls.convert_humanities(grade)
                # 여기서는 단순 평균이므로 등급을 숫자로
                score = ord(converted) - ord('A') + 1  # A=1, B=2, ...
            elif major_type == 'science':
                result = cls.convert_science(grade)
                score = result['score']
            else:  # medical
                score = cls.convert_medical(grade)

            total_score += score * credit
            total_credit += credit

        if total_credit == 0:
            return 0

        return round(total_score / total_credit, 2)


# ==================== 다른 대학 추가 시 ====================

class SampleUniversityConverter:
    """샘플 대학 변환기 (템플릿)"""

    @classmethod
    def convert(cls, grade: int) -> any:
        """대학별 변환 로직"""
        pass


# ==================== 통합 인터페이스 ====================

class UniversityConverter:
    """대학별 변환기 통합 인터페이스"""

    CONVERTERS = {
        'gachon': GachonConverter,
        # 'yonsei': YonseiConverter,  # 나중에 추가
        # 'korea': KoreaConverter,
    }

    @classmethod
    def get_converter(cls, university_name: str):
        """
        대학명으로 변환기 가져오기

        Args:
            university_name: 대학명 (소문자)

        Returns:
            Converter class

        Raises:
            ValueError: 지원하지 않는 대학
        """
        converter = cls.CONVERTERS.get(university_name.lower())
        if not converter:
            raise ValueError(
                f"Unsupported university: {university_name}. "
                f"Available: {list(cls.CONVERTERS.keys())}"
            )
        return converter

    @classmethod
    def convert(
        cls,
        university_name: str,
        grade: int,
        major_type: str = 'humanities'
    ) -> any:
        """
        대학별 등급 변환

        Args:
            university_name: 대학명
            grade: 석차등급
            major_type: 전형 타입

        Returns:
            변환 결과
        """
        converter = cls.get_converter(university_name)

        if university_name.lower() == 'gachon':
            if major_type == 'humanities':
                return converter.convert_humanities(grade)
            elif major_type == 'science':
                return converter.convert_science(grade)
            elif major_type == 'medical':
                return converter.convert_medical(grade)

        return None
