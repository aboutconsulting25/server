from django.contrib import admin
from .models import ConsultationReport, ConsultationSession


@admin.register(ConsultationReport)
class ConsultationReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'consultant', 'report_type', 'status', 'sent_at', 'created_at']
    list_filter = ['report_type', 'status', 'created_at']
    search_fields = ['title', 'student__name', 'consultant__name']
    ordering = ['-created_at']
    readonly_fields = ['sent_at', 'created_at', 'updated_at']


@admin.register(ConsultationSession)
class ConsultationSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'consultant', 'session_type', 'session_date', 'duration_minutes', 'created_at']
    list_filter = ['session_type', 'session_date', 'created_at']
    search_fields = ['student__name', 'consultant__name']
    ordering = ['-session_date']
    readonly_fields = ['created_at', 'updated_at']
