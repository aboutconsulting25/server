from django.test import TestCase
from apps.grades.utils import (
    convert_9_to_5, convert_5_to_9,
    calculate_rank_from_grade, calculate_grade_from_rank
)


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
