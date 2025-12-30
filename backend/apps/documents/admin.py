from django.contrib import admin
from .models import Document, DocumentVersion


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ['version_number', 'created_by', 'created_at']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'document_type', 'status', 'uploaded_by', 'created_at']
    list_filter = ['document_type', 'status', 'created_at']
    search_fields = ['title', 'student__name']
    ordering = ['-created_at']
    readonly_fields = ['file_size', 'mime_type', 'uploaded_by', 'created_at', 'updated_at']
    inlines = [DocumentVersionInline]


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ['document', 'version_number', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['document__title']
    ordering = ['-created_at']
    readonly_fields = ['created_by', 'created_at']
