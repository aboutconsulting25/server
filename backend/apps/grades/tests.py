from django.test import TestCase
from apps.grades.utils import (
    convert_9_to_5, convert_5_to_9,
    calculate_rank_from_grade, calculate_grade_from_rank
)
from apps.grades.university_converters import GachonConverter, UniversityConverter


class GradeConversionTestCase(TestCase):
    def test_convert_9_to_5_integers(self):
        """정수 등급 변환 (9등급제 → 5등급제)"""
        # 9등급제 1등급 (상위 4%) → 5등급제 1등급
        self.assertAlmostEqual(convert_9_to_5(1.0), 1.0, places=1)
        # 9등급제 2등급 (상위 11%) → 5등급제 1.04등급 (10%~34% 범위의 앞쪽)
        self.assertAlmostEqual(convert_9_to_5(2.0), 1.04, places=1)
        # 9등급제 5등급 (상위 60%) → 5등급제 2.81등급 (34%~66% 범위의 뒤쪽)
        self.assertAlmostEqual(convert_9_to_5(5.0), 2.81, places=1)

    def test_convert_5_to_9_integers(self):
        """5등급제 → 9등급제"""
        # 5등급제 1등급 (상위 10%) → 9등급제 1.86등급 (4%~11% 범위의 뒤쪽)
        self.assertAlmostEqual(convert_5_to_9(1.0), 1.86, places=1)
        # 5등급제 2등급 (상위 34%) → 9등급제 3.65등급 (23%~40% 범위의 중간)
        self.assertAlmostEqual(convert_5_to_9(2.0), 3.65, places=1)

    def test_rank_calculation(self):
        """등급 → 등수 계산"""
        # 9등급제 1등급 = 상위 4% = 250명 중 10등
        self.assertEqual(calculate_rank_from_grade(1.0, 250, '9'), 10)
        # 5등급제 1등급 = 상위 10% = 250명 중 25등
        self.assertEqual(calculate_rank_from_grade(1.0, 250, '5'), 25)


class GachonConverterTestCase(TestCase):
    """가천대 등급 변환 테스트"""

    def test_humanities_conversion(self):
        """인문계열 변환"""
        self.assertEqual(GachonConverter.convert_humanities(1), 'A')
        self.assertEqual(GachonConverter.convert_humanities(2), 'A')
        self.assertEqual(GachonConverter.convert_humanities(3), 'B')
        self.assertEqual(GachonConverter.convert_humanities(4), 'B')
        self.assertEqual(GachonConverter.convert_humanities(5), 'C')
        self.assertEqual(GachonConverter.convert_humanities(6), 'C')
        self.assertEqual(GachonConverter.convert_humanities(7), 'D')
        self.assertEqual(GachonConverter.convert_humanities(8), 'D')
        self.assertEqual(GachonConverter.convert_humanities(9), 'E')

    def test_science_conversion(self):
        """자연계열 변환"""
        result = GachonConverter.convert_science(1)
        self.assertEqual(result['converted_grade'], 'A')
        self.assertEqual(result['score'], 100)

        result = GachonConverter.convert_science(2)
        self.assertEqual(result['converted_grade'], 'B')
        self.assertEqual(result['score'], 99.5)

        result = GachonConverter.convert_science(3)
        self.assertEqual(result['converted_grade'], 'B')
        self.assertEqual(result['score'], 99.5)

        result = GachonConverter.convert_science(4)
        self.assertEqual(result['converted_grade'], 'C')
        self.assertEqual(result['score'], 99)

        result = GachonConverter.convert_science(8)
        self.assertEqual(result['converted_grade'], 'E')
        self.assertEqual(result['score'], 70)

    def test_medical_conversion(self):
        """의예과 변환"""
        self.assertEqual(GachonConverter.convert_medical(1), 100)
        self.assertEqual(GachonConverter.convert_medical(2), 99.5)
        self.assertEqual(GachonConverter.convert_medical(3), 99)
        self.assertEqual(GachonConverter.convert_medical(4), 98.5)
        self.assertEqual(GachonConverter.convert_medical(5), 98)
        self.assertEqual(GachonConverter.convert_medical(6), 97.5)
        self.assertEqual(GachonConverter.convert_medical(7), 85)
        self.assertEqual(GachonConverter.convert_medical(8), 60)
        self.assertEqual(GachonConverter.convert_medical(9), 30)

    def test_gpa_calculation(self):
        """환산 평균 계산"""
        grades = [
            {'grade': 2, 'credit': 3, 'year': 2},
            {'grade': 3, 'credit': 4, 'year': 2},
        ]
        gpa = GachonConverter.calculate_gpa(grades, 'science')
        # (99.5*3 + 99.5*4) / 7 = 99.5
        self.assertAlmostEqual(gpa, 99.5, places=1)

    def test_ignore_first_year(self):
        """1학년 성적 제외"""
        grades = [
            {'grade': 1, 'credit': 3, 'year': 1},  # 제외
            {'grade': 2, 'credit': 3, 'year': 2},
        ]
        gpa = GachonConverter.calculate_gpa(grades, 'science')
        # 2학년 2등급만 = 99.5
        self.assertEqual(gpa, 99.5)

    def test_invalid_grade(self):
        """잘못된 등급 입력"""
        with self.assertRaises(ValueError):
            GachonConverter.convert_humanities(0)

        with self.assertRaises(ValueError):
            GachonConverter.convert_humanities(10)

        with self.assertRaises(ValueError):
            GachonConverter.convert_science(0)

        with self.assertRaises(ValueError):
            GachonConverter.convert_medical(10)


class UniversityConverterTestCase(TestCase):
    """대학별 변환기 통합 인터페이스 테스트"""

    def test_get_converter(self):
        """변환기 가져오기"""
        converter = UniversityConverter.get_converter('gachon')
        self.assertEqual(converter, GachonConverter)

    def test_unsupported_university(self):
        """지원하지 않는 대학"""
        with self.assertRaises(ValueError):
            UniversityConverter.get_converter('unsupported')

    def test_convert_gachon_humanities(self):
        """가천대 인문계열 변환"""
        result = UniversityConverter.convert('gachon', 2, 'humanities')
        self.assertEqual(result, 'A')

    def test_convert_gachon_science(self):
        """가천대 자연계열 변환"""
        result = UniversityConverter.convert('gachon', 2, 'science')
        self.assertEqual(result['converted_grade'], 'B')
        self.assertEqual(result['score'], 99.5)

    def test_convert_gachon_medical(self):
        """가천대 의예과 변환"""
        result = UniversityConverter.convert('gachon', 5, 'medical')
        self.assertEqual(result, 98)
