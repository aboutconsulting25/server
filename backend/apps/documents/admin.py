from django.contrib import admin
from .models import Document, DocumentAnalysis


class DocumentAnalysisInline(admin.TabularInline):
    model = DocumentAnalysis
    extra = 0
    readonly_fields = ['analysis_version', 'status', 'started_at', 'completed_at', 'created_at']
    fields = ['analysis_version', 'status', 'started_at', 'completed_at']
    can_delete = False


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'document_type', 'version', 'is_latest', 'status', 'uploaded_by', 'created_at']
    list_filter = ['document_type', 'status', 'is_latest', 'created_at']
    search_fields = ['title', 'student__name']
    ordering = ['-created_at']
    readonly_fields = ['version', 'file_size', 'mime_type', 'uploaded_by', 'created_at', 'updated_at']
    inlines = [DocumentAnalysisInline]


@admin.register(DocumentAnalysis)
class DocumentAnalysisAdmin(admin.ModelAdmin):
    list_display = ['document', 'student', 'analysis_version', 'status', 'started_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['document__title', 'student__name']
    ordering = ['-created_at']
    readonly_fields = ['analysis_version', 'started_at', 'completed_at', 'created_at', 'updated_at']
    fieldsets = (
        ('기본 정보', {
            'fields': ('document', 'student', 'analysis_version', 'status')
        }),
        ('분석 결과', {
            'fields': ('ocr_result', 'analysis_result')
        }),
        ('에러 정보', {
            'fields': ('error_message',)
        }),
        ('타임스탬프', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at')
        }),
    )


# 기존 DocumentVersion 관련 코드 (주석 처리)
# from .models import DocumentVersion
#
# class DocumentVersionInline(admin.TabularInline):
#     model = DocumentVersion
#     extra = 0
#     readonly_fields = ['version_number', 'created_by', 'created_at']
#
# @admin.register(DocumentVersion)
# class DocumentVersionAdmin(admin.ModelAdmin):
#     list_display = ['document', 'version_number', 'created_by', 'created_at']
#     list_filter = ['created_at']
#     search_fields = ['document__title']
#     ordering = ['-created_at']
#     readonly_fields = ['created_by', 'created_at']
