import uuid
from django.db import models
from django.conf import settings


class Document(models.Model):
    """서류 관리"""
    DOCUMENT_TYPE_CHOICES = (
        ('TRANSCRIPT', '생활기록부'),
        ('REPORT', '성적표'),
        ('RECOMMENDATION', '추천서'),
        ('ESSAY', '자기소개서'),
        ('PORTFOLIO', '포트폴리오'),
        ('CERTIFICATE', '수상/자격증'),
        ('OTHER', '기타'),
    )

    STATUS_CHOICES = (
        ('UPLOADED', '업로드됨'),
        ('PROCESSING', '처리중'),
        ('COMPLETED', '완료'),
        ('FAILED', '실패'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='학생'
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='서류 유형'
    )
    title = models.CharField(max_length=200, verbose_name='제목')
    file = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name='파일')
    file_size = models.BigIntegerField(default=0, verbose_name='파일 크기 (bytes)')
    mime_type = models.CharField(max_length=100, blank=True, verbose_name='MIME 타입')

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='UPLOADED',
        verbose_name='처리 상태'
    )

    # OCR 및 AI 분석 결과
    ocr_text = models.TextField(blank=True, verbose_name='OCR 추출 텍스트')
    ai_analysis = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='AI 분석 결과',
        help_text='AI 분석 결과 JSON 데이터'
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
        verbose_name='업로드한 사용자'
    )

    notes = models.TextField(blank=True, verbose_name='메모')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents'
        verbose_name = '서류'
        verbose_name_plural = '서류'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} - {self.get_document_type_display()} - {self.title}"


class DocumentVersion(models.Model):
    """서류 버전 관리"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name='서류'
    )
    version_number = models.IntegerField(verbose_name='버전 번호')
    file = models.FileField(upload_to='document_versions/%Y/%m/%d/', verbose_name='파일')
    file_size = models.BigIntegerField(default=0, verbose_name='파일 크기 (bytes)')

    changes_description = models.TextField(blank=True, verbose_name='변경 내용')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_versions',
        verbose_name='생성한 사용자'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_versions'
        verbose_name = '서류 버전'
        verbose_name_plural = '서류 버전'
        ordering = ['-version_number']
        unique_together = [['document', 'version_number']]

    def __str__(self):
        return f"{self.document.title} - v{self.version_number}"
