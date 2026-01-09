import uuid
from django.db import models
from django.conf import settings


class Document(models.Model):
    """서류 관리"""
    DOCUMENT_TYPE_CHOICES = (
        ('생기부', '생활기록부'),
        ('모의고사', '모의고사 성적표'),
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
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        default='생기부',
        verbose_name='문서 타입'
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

    # 버전 관리
    version = models.IntegerField(default=1, verbose_name='버전')
    is_latest = models.BooleanField(default=True, verbose_name='최신 버전 여부')

    # OCR 및 AI 분석 결과
    # ocr_text = models.TextField(blank=True, verbose_name='OCR 추출 텍스트')
    # ai_analysis = models.JSONField(
    #     default=dict,
    #     blank=True,
    #     verbose_name='AI 분석 결과',
    #     help_text='AI 분석 결과 JSON 데이터'
    # )

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
        indexes = [
            models.Index(fields=['student', 'is_latest']),
            models.Index(fields=['student', 'version']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.get_document_type_display()} - {self.title}"


# class DocumentVersion(models.Model):
#     """서류 버전 관리"""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     document = models.ForeignKey(
#         Document,
#         on_delete=models.CASCADE,
#         related_name='versions',
#         verbose_name='서류'
#     )
#     version_number = models.IntegerField(verbose_name='버전 번호')
#     file = models.FileField(upload_to='document_versions/%Y/%m/%d/', verbose_name='파일')
#     file_size = models.BigIntegerField(default=0, verbose_name='파일 크기 (bytes)')

#     changes_description = models.TextField(blank=True, verbose_name='변경 내용')
#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name='created_versions',
#         verbose_name='생성한 사용자'
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = 'document_versions'
#         verbose_name = '서류 버전'
#         verbose_name_plural = '서류 버전'
#         ordering = ['-version_number']
#         unique_together = [['document', 'version_number']]

#     def __str__(self):
#         return f"{self.document.title} - v{self.version_number}"


class DocumentAnalysis(models.Model):
    """
    생기부 분석 이력 추적
    - 하나의 Document에 여러 번 분석 가능
    - analysis_version으로 분석 버전 관리
    """
    STATUS_CHOICES = (
        ('PENDING', '대기중'),
        ('PROCESSING', '처리중'),
        ('COMPLETED', '완료'),
        ('FAILED', '실패'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # 연관 관계
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='analyses',
        verbose_name='문서'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='document_analyses',
        verbose_name='학생'
    )

    # 분석 버전
    analysis_version = models.IntegerField(
        default=1,
        verbose_name='분석 버전',
        help_text='같은 문서를 여러 번 분석할 수 있음'
    )

    # 상태
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name='분석 상태'
    )

    # OCR 결과
    ocr_result = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='OCR 결과',
        help_text='''
        {
            "자율활동": "...",
            "동아리활동": "...",
            "봉사활동": "...",
            "진로활동": "...",
            "교과세특": {
                "국어": "...",
                "수학": "..."
            }
        }
        '''
    )

    # AI 분석 결과 - 생기부 분석
    analysis_result = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='AI 분석 결과',
        help_text='''
        생기부 분석 결과 (AI 모듈 output):
        {
            "강점요약": {"첫번째_강점": "", "두번째_강점": "", "세번째_강점": ""},
            "약점요약": {"첫번째_약점": "", "두번째_약점": "", "세번째_약점": ""},
            "생기부_진단개요": {"한줄 요약": "", "본문": ""},
            "진로적합성_강화방안": {
                "강화방안": {...},
                "비교과_지도필요_영역": {...},
                "전공_관련_탐구_및_독서활동": {...}
            }
        }
        '''
    )

    # 에러 정보
    error_message = models.TextField(blank=True, verbose_name='에러 메시지')

    # 타임스탬프
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='분석 시작 시각')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='분석 완료 시각')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document_analysis'
        verbose_name = '문서 분석'
        verbose_name_plural = '문서 분석'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document']),
            models.Index(fields=['student']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.document} - 분석 v{self.analysis_version}"
