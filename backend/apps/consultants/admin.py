from django.contrib import admin
from .models import Consultant


@admin.register(Consultant)
class ConsultantAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'specialization', 'max_students', 'get_current_students', 'created_at']
    list_filter = ['specialization', 'created_at']
    search_fields = ['name', 'user__username', 'specialization']
    ordering = ['name']

    def get_current_students(self, obj):
        return obj.current_students
    get_current_students.short_description = '현재 담당 학생 수'
