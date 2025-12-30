import uuid
from django.db import models
from django.conf import settings


class ConsultationReport(models.Model):
    """컨설팅 리포트"""
    REPORT_TYPE_CHOICES = (
        ('INITIAL', '초기 상담'),
        ('PROGRESS', '진행 상황'),
        ('MONTHLY', '월간 리포트'),
        ('FINAL', '최종 리포트'),
        ('SPECIAL', '특별 리포트'),
    )

    STATUS_CHOICES = (
        ('DRAFT', '작성중'),
        ('COMPLETED', '완료'),
        ('SENT', '전송됨'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='consultation_reports',
        verbose_name='학생'
    )
    consultant = models.ForeignKey(
        'consultants.Consultant',
        on_delete=models.SET_NULL,
        null=True,
        related_name='consultation_reports',
        verbose_name='컨설턴트'
    )

    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        verbose_name='리포트 유형'
    )
    title = models.CharField(max_length=200, verbose_name='제목')

    # 리포트 내용
    summary = models.TextField(blank=True, verbose_name='요약')
    content = models.TextField(verbose_name='내용')

    # 학생 현황 분석
    current_status = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='현재 상황',
        help_text='성적, 활동 등 현재 상황'
    )

    # 목표 대학 분석
    university_analysis = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='목표 대학 분석',
        help_text='지망 대학 합격 가능성 분석'
    )

    # 개선 사항 및 전략
    improvement_plan = models.TextField(blank=True, verbose_name='개선 계획')
    action_items = models.JSONField(
        default=list,
        blank=True,
        verbose_name='실행 항목',
        help_text='구체적인 실행 항목 리스트'
    )

    # AI 분석 결과
    ai_insights = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='AI 인사이트',
        help_text='AI 분석을 통한 추가 인사이트'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        verbose_name='상태'
    )

    # 리포트 파일 (선택적)
    report_file = models.FileField(
        upload_to='reports/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='리포트 파일',
        help_text='PDF 등 생성된 리포트 파일'
    )

    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='전송 일시')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consultation_reports'
        verbose_name = '컨설팅 리포트'
        verbose_name_plural = '컨설팅 리포트'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} - {self.get_report_type_display()} - {self.title}"


class ConsultationSession(models.Model):
    """상담 세션 기록"""
    SESSION_TYPE_CHOICES = (
        ('ONLINE', '온라인'),
        ('OFFLINE', '오프라인'),
        ('PHONE', '전화'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='consultation_sessions',
        verbose_name='학생'
    )
    consultant = models.ForeignKey(
        'consultants.Consultant',
        on_delete=models.SET_NULL,
        null=True,
        related_name='consultation_sessions',
        verbose_name='컨설턴트'
    )

    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPE_CHOICES,
        verbose_name='상담 유형'
    )
    session_date = models.DateTimeField(verbose_name='상담 일시')
    duration_minutes = models.IntegerField(default=60, verbose_name='소요 시간 (분)')

    # 상담 내용
    topics_discussed = models.JSONField(
        default=list,
        blank=True,
        verbose_name='논의 주제',
        help_text='상담에서 논의된 주제 리스트'
    )
    notes = models.TextField(verbose_name='상담 내용')

    # 다음 액션
    next_actions = models.TextField(blank=True, verbose_name='다음 액션')
    next_session_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='다음 상담 예정일'
    )

    # 첨부 파일
    attachments = models.JSONField(
        default=list,
        blank=True,
        verbose_name='첨부 파일',
        help_text='상담 관련 첨부 파일 정보'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consultation_sessions'
        verbose_name = '상담 세션'
        verbose_name_plural = '상담 세션'
        ordering = ['-session_date']

    def __str__(self):
        return f"{self.student.name} - {self.session_date.strftime('%Y-%m-%d')} - {self.get_session_type_display()}"
