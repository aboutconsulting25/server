import uuid
from django.db import models
from django.conf import settings


class Student(models.Model):
    """학생 정보"""
    STATUS_CHOICES = (
        ('ACTIVE', '활성'),
        ('INACTIVE', '비활성'),
        ('GRADUATED', '졸업'),
    )

    GRADE_CHOICES = (
        ('1', '고1'),
        ('2', '고2'),
        ('3', '고3'),
        ('GRADUATED', '졸업생'),
    )

    MAJOR_TRACK_CHOICES = (
        ('HUMANITIES', '인문계'),
        ('SCIENCE', '자연계'),
        ('ART', '예체능'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='이름')
    student_code = models.CharField(max_length=50, unique=True, verbose_name='학생 코드')
    high_school = models.ForeignKey(
        'schools.HighSchool',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name='고등학교'
    )
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, verbose_name='학년')

    # MVP: 계열 추가
    major_track = models.CharField(
        max_length=20,
        choices=MAJOR_TRACK_CHOICES,
        blank=True,
        verbose_name='계열',
        help_text='인문계/자연계/예체능'
    )

    # MVP: 희망 대학/학과 (텍스트 입력, 추후 FK로 전환 예정)
    desired_universities_text = models.JSONField(
        default=list,
        blank=True,
        verbose_name='희망 대학 목록 (임시)',
        help_text='''
        [
            {"university": "서울대학교", "department": "컴퓨터공학과"},
            {"university": "연세대학교", "department": "전기전자공학과"},
            ...
        ]
        추후 University/Department 모델과 FK 연결 예정
        '''
    )

    phone = models.CharField(max_length=20, blank=True, verbose_name='연락처')
    parent_phone = models.CharField(max_length=20, blank=True, verbose_name='학부모 연락처')

    consultant = models.ForeignKey(
        'consultants.Consultant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name='담당 컨설턴트'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        verbose_name='상태'
    )

    notes = models.TextField(blank=True, verbose_name='메모')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'
        verbose_name = '학생'
        verbose_name_plural = '학생'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.student_code})"


class StudentDesiredUniversity(models.Model):
    """학생 지망 대학"""
    PRIORITY_CHOICES = (
        ('FIRST', '1지망'),
        ('SECOND', '2지망'),
        ('THIRD', '3지망'),
        ('SAFETY', '안전'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='desired_universities',
        verbose_name='학생'
    )
    university = models.ForeignKey(
        'schools.University',
        on_delete=models.CASCADE,
        related_name='desired_by_students',
        verbose_name='대학'
    )
    department = models.CharField(max_length=100, verbose_name='학과')
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        verbose_name='우선순위'
    )
    admission_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='전형 유형',
        help_text='예: 학생부종합, 학생부교과, 논술 등'
    )
    notes = models.TextField(blank=True, verbose_name='메모')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_desired_universities'
        verbose_name = '학생 지망 대학'
        verbose_name_plural = '학생 지망 대학'
        unique_together = [['student', 'university', 'department']]
        ordering = ['priority']

    def __str__(self):
        return f"{self.student.name} - {self.university.name} {self.department} ({self.priority})"
