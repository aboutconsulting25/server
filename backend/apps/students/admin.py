from django.contrib import admin
from .models import Student, StudentDesiredUniversity


class StudentDesiredUniversityInline(admin.TabularInline):
    model = StudentDesiredUniversity
    extra = 1


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_code', 'high_school', 'grade', 'consultant', 'status', 'created_at']
    list_filter = ['grade', 'status', 'high_school', 'consultant', 'created_at']
    search_fields = ['name', 'student_code']
    ordering = ['-created_at']
    inlines = [StudentDesiredUniversityInline]


@admin.register(StudentDesiredUniversity)
class StudentDesiredUniversityAdmin(admin.ModelAdmin):
    list_display = ['student', 'university', 'department', 'priority', 'admission_type', 'created_at']
    list_filter = ['priority', 'admission_type', 'university', 'created_at']
    search_fields = ['student__name', 'university__name', 'department']
    ordering = ['student', 'priority']
