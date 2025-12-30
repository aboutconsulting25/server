import uuid
from django.db import models
from django.conf import settings


class Consultant(models.Model):
    """컨설턴트 상세 정보"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consultant_profile',
        verbose_name='사용자'
    )
    name = models.CharField(max_length=100, verbose_name='이름')
    phone = models.CharField(max_length=20, verbose_name='연락처')
    specialization = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='전문 분야',
        help_text='예: 이공계, 인문계, 의대 등'
    )
    max_students = models.IntegerField(default=30, verbose_name='최대 담당 학생 수')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consultants'
        verbose_name = '컨설턴트'
        verbose_name_plural = '컨설턴트'

    def __str__(self):
        return f"{self.name} ({self.specialization})"

    @property
    def current_students(self):
        """현재 담당 학생 수"""
        return self.students.filter(status='ACTIVE').count()
