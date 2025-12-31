import uuid
from django.db import models
from decimal import Decimal
from .utils import convert_9_to_5, convert_5_to_9


class Grade(models.Model):
    """학생 성적 관리"""
    SEMESTER_CHOICES = (
        ('1-1', '1학년 1학기'),
        ('1-2', '1학년 2학기'),
        ('2-1', '2학년 1학기'),
        ('2-2', '2학년 2학기'),
        ('3-1', '3학년 1학기'),
        ('3-2', '3학년 2학기'),
    )

    EXAM_TYPE_CHOICES = (
        ('MIDTERM', '중간고사'),
        ('FINAL', '기말고사'),
        ('MOCK', '모의고사'),
        ('OVERALL', '전체'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='학생'
    )
    semester = models.CharField(
        max_length=10,
        choices=SEMESTER_CHOICES,
        verbose_name='학기'
    )
    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPE_CHOICES,
        verbose_name='시험 유형'
    )

    # 내신 성적
    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='평균 등급',
        help_text='전 과목 평균 등급'
    )

    # 수능 관련 성적
    korean_score = models.IntegerField(null=True, blank=True, verbose_name='국어 점수')
    korean_grade = models.IntegerField(null=True, blank=True, verbose_name='국어 등급')

    math_score = models.IntegerField(null=True, blank=True, verbose_name='수학 점수')
    math_grade = models.IntegerField(null=True, blank=True, verbose_name='수학 등급')

    english_score = models.IntegerField(null=True, blank=True, verbose_name='영어 점수')
    english_grade = models.IntegerField(null=True, blank=True, verbose_name='영어 등급')

    science1_score = models.IntegerField(null=True, blank=True, verbose_name='과학1 점수')
    science1_grade = models.IntegerField(null=True, blank=True, verbose_name='과학1 등급')

    science2_score = models.IntegerField(null=True, blank=True, verbose_name='과학2 점수')
    science2_grade = models.IntegerField(null=True, blank=True, verbose_name='과학2 등급')

    history_score = models.IntegerField(null=True, blank=True, verbose_name='한국사 점수')
    history_grade = models.IntegerField(null=True, blank=True, verbose_name='한국사 등급')

    # 총점 및 통계
    total_score = models.IntegerField(null=True, blank=True, verbose_name='총점')
    percentile = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='백분위',
        help_text='상위 몇 %'
    )

    notes = models.TextField(blank=True, verbose_name='메모')

    # 버전 관리
    version = models.IntegerField(
        default=1,
        verbose_name='버전'
    )
    is_latest = models.BooleanField(
        default=True,
        verbose_name='최신 버전 여부'
    )
    correction_reason = models.TextField(
        blank=True,
        verbose_name='정정 사유',
        help_text='성적 정정 시 사유 입력'
    )
    corrected_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='corrected_grades',
        verbose_name='정정한 사용자'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'grades'
        verbose_name = '성적'
        verbose_name_plural = '성적'
        ordering = ['-created_at']
        unique_together = [['student', 'semester', 'exam_type', 'version']]
        indexes = [
            models.Index(fields=['student', 'semester']),
            models.Index(fields=['student', 'exam_type']),
            models.Index(fields=['student', 'is_latest']),
            models.Index(fields=['is_latest']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.get_semester_display()} - {self.get_exam_type_display()}"

    def save(self, *args, **kwargs):
        """저장 시 자동 버전 관리"""
        if not self.pk:  # 새로 생성되는 경우
            # 같은 학생/학기/시험의 기존 성적을 is_latest=False로
            if self.is_latest:
                Grade.objects.filter(
                    student=self.student,
                    semester=self.semester,
                    exam_type=self.exam_type,
                    is_latest=True
                ).update(is_latest=False)

            # 마지막 버전 번호 +1
            last_grade = Grade.objects.filter(
                student=self.student,
                semester=self.semester,
                exam_type=self.exam_type
            ).order_by('-version').first()

            if last_grade:
                self.version = last_grade.version + 1

        super().save(*args, **kwargs)

    @property
    def average_grade(self):
        """전체 평균 등급 계산"""
        grades = [
            self.korean_grade,
            self.math_grade,
            self.english_grade,
            self.science1_grade,
            self.science2_grade,
            self.history_grade,
        ]
        valid_grades = [g for g in grades if g is not None]
        if valid_grades:
            return sum(valid_grades) / len(valid_grades)
        return None

    # 등급 변환 프로퍼티 (9등급제 ↔ 5등급제)
    @property
    def korean_grade_5(self):
        """국어 등급을 5등급제로 변환"""
        if self.korean_grade:
            return convert_9_to_5(float(self.korean_grade))
        return None

    @property
    def korean_grade_9(self):
        """국어 등급 (9등급제)"""
        return float(self.korean_grade) if self.korean_grade else None

    @property
    def math_grade_5(self):
        """수학 등급을 5등급제로 변환"""
        if self.math_grade:
            return convert_9_to_5(float(self.math_grade))
        return None

    @property
    def math_grade_9(self):
        """수학 등급 (9등급제)"""
        return float(self.math_grade) if self.math_grade else None

    @property
    def english_grade_5(self):
        """영어 등급을 5등급제로 변환"""
        if self.english_grade:
            return convert_9_to_5(float(self.english_grade))
        return None

    @property
    def english_grade_9(self):
        """영어 등급 (9등급제)"""
        return float(self.english_grade) if self.english_grade else None

    @property
    def science1_grade_5(self):
        """과학1 등급을 5등급제로 변환"""
        if self.science1_grade:
            return convert_9_to_5(float(self.science1_grade))
        return None

    @property
    def science1_grade_9(self):
        """과학1 등급 (9등급제)"""
        return float(self.science1_grade) if self.science1_grade else None

    @property
    def science2_grade_5(self):
        """과학2 등급을 5등급제로 변환"""
        if self.science2_grade:
            return convert_9_to_5(float(self.science2_grade))
        return None

    @property
    def science2_grade_9(self):
        """과학2 등급 (9등급제)"""
        return float(self.science2_grade) if self.science2_grade else None

    @property
    def history_grade_5(self):
        """한국사 등급을 5등급제로 변환"""
        if self.history_grade:
            return convert_9_to_5(float(self.history_grade))
        return None

    @property
    def history_grade_9(self):
        """한국사 등급 (9등급제)"""
        return float(self.history_grade) if self.history_grade else None


class SubjectGrade(models.Model):
    """과목별 세부 성적"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name='subject_grades',
        verbose_name='성적'
    )
    subject_name = models.CharField(max_length=50, verbose_name='과목명')

    # 내신 성적
    raw_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='원점수'
    )
    standard_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='표준점수'
    )
    grade_rank = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='등급',
        help_text='1~9등급'
    )
    percentile = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='백분위'
    )

    # 반 정보
    class_rank = models.IntegerField(null=True, blank=True, verbose_name='반 석차')
    class_total = models.IntegerField(null=True, blank=True, verbose_name='반 인원')

    # 학년 정보
    grade_rank_in_school = models.IntegerField(null=True, blank=True, verbose_name='학년 석차')
    grade_total_in_school = models.IntegerField(null=True, blank=True, verbose_name='학년 인원')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subject_grades'
        verbose_name = '과목별 성적'
        verbose_name_plural = '과목별 성적'
        ordering = ['subject_name']
        unique_together = [['grade', 'subject_name']]

    def __str__(self):
        return f"{self.grade.student.name} - {self.subject_name}"
