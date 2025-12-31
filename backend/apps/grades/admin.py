from django.contrib import admin
from .models import Grade, SubjectGrade


class SubjectGradeInline(admin.TabularInline):
    model = SubjectGrade
    extra = 1


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'semester', 'exam_type',
        'version', 'is_latest',
        'gpa', 'total_score', 'created_at'
    ]
    list_filter = [
        'semester', 'exam_type',
        'is_latest',
    ]
    search_fields = ['student__name']
    readonly_fields = [
        'id', 'version', 'average_grade',
        'created_at', 'updated_at'
    ]
    ordering = ['-created_at']
    inlines = [SubjectGradeInline]

    fieldsets = (
        ('기본 정보', {
            'fields': ('student', 'semester', 'exam_type')
        }),
        ('버전 정보', {
            'fields': ('version', 'is_latest', 'correction_reason', 'corrected_by')
        }),
        ('성적', {
            'fields': (
                'gpa',
                ('korean_score', 'korean_grade'),
                ('math_score', 'math_grade'),
                ('english_score', 'english_grade'),
                ('science1_score', 'science1_grade'),
                ('science2_score', 'science2_grade'),
                ('history_score', 'history_grade'),
                'total_score', 'percentile'
            )
        }),
        ('메타', {
            'fields': ('notes', 'created_at', 'updated_at')
        })
    )


@admin.register(SubjectGrade)
class SubjectGradeAdmin(admin.ModelAdmin):
    list_display = ['grade', 'subject_name', 'raw_score', 'grade_rank', 'percentile', 'class_rank', 'created_at']
    list_filter = ['subject_name', 'created_at']
    search_fields = ['grade__student__name', 'subject_name']
    ordering = ['-created_at']
