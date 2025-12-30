import uuid
from django.db import models


class HighSchool(models.Model):
    """고등학교 마스터 데이터"""
    SCHOOL_TYPE_CHOICES = (
        ('일반고', '일반고'),
        ('특목고', '특목고'),
        ('자사고', '자율형사립고'),
        ('특성화고', '특성화고'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name='학교명')
    region = models.CharField(max_length=50, verbose_name='지역', db_index=True)
    district = models.CharField(max_length=50, verbose_name='구/군', blank=True)
    school_type = models.CharField(
        max_length=20,
        choices=SCHOOL_TYPE_CHOICES,
        default='일반고',
        verbose_name='학교 유형'
    )
    ranking = models.IntegerField(null=True, blank=True, verbose_name='전국 순위')
    statistics = models.JSONField(default=dict, blank=True, verbose_name='진학 통계')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'high_schools'
        verbose_name = '고등학교'
        verbose_name_plural = '고등학교'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.region})"


class University(models.Model):
    """대학교 마스터 데이터"""
    UNIVERSITY_TYPE_CHOICES = (
        ('국립', '국립'),
        ('사립', '사립'),
        ('의대', '의과대학'),
        ('교대', '교육대학'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name='대학명')
    university_type = models.CharField(
        max_length=20,
        choices=UNIVERSITY_TYPE_CHOICES,
        default='사립',
        verbose_name='대학 유형'
    )
    ranking = models.IntegerField(null=True, blank=True, verbose_name='순위')
    region = models.CharField(max_length=50, verbose_name='지역')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='추가 정보')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'universities'
        verbose_name = '대학교'
        verbose_name_plural = '대학교'
        ordering = ['ranking', 'name']

    def __str__(self):
        return self.name


class UniversityAdmissionCriteria(models.Model):
    """대학별 입학 전형 정보"""
    ADMISSION_TYPE_CHOICES = (
        ('수시', '수시'),
        ('정시', '정시'),
        ('특기자', '특기자'),
        ('학생부종합', '학생부종합'),
        ('학생부교과', '학생부교과'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='admission_criteria',
        verbose_name='대학'
    )
    department = models.CharField(max_length=100, verbose_name='학과명')
    admission_type = models.CharField(
        max_length=20,
        choices=ADMISSION_TYPE_CHOICES,
        verbose_name='전형 유형'
    )
    year = models.IntegerField(verbose_name='전형 연도')
    criteria = models.JSONField(default=dict, verbose_name='전형 상세')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'university_admission_criteria'
        verbose_name = '대학 입학 전형'
        verbose_name_plural = '대학 입학 전형'
        ordering = ['-year', 'university', 'department']
        unique_together = ['university', 'department', 'admission_type', 'year']

    def __str__(self):
        return f"{self.university.name} {self.department} {self.admission_type} ({self.year})"
