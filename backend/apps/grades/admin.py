from django.contrib import admin
from .models import Grade, SubjectGrade


class SubjectGradeInline(admin.TabularInline):
    model = SubjectGrade
    extra = 1


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'semester', 'exam_type', 'gpa', 'total_score', 'percentile', 'created_at']
    list_filter = ['semester', 'exam_type', 'created_at']
    search_fields = ['student__name']
    ordering = ['-created_at']
    inlines = [SubjectGradeInline]


@admin.register(SubjectGrade)
class SubjectGradeAdmin(admin.ModelAdmin):
    list_display = ['grade', 'subject_name', 'raw_score', 'grade_rank', 'percentile', 'class_rank', 'created_at']
    list_filter = ['subject_name', 'created_at']
    search_fields = ['grade__student__name', 'subject_name']
    ordering = ['-created_at']
