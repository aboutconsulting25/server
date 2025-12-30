from django.contrib import admin
from .models import HighSchool, University, UniversityAdmissionCriteria


@admin.register(HighSchool)
class HighSchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'school_type', 'created_at']
    list_filter = ['region', 'school_type', 'created_at']
    search_fields = ['name', 'region']
    ordering = ['name']


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'university_type', 'ranking', 'created_at']
    list_filter = ['region', 'university_type', 'created_at']
    search_fields = ['name', 'region']
    ordering = ['ranking', 'name']


@admin.register(UniversityAdmissionCriteria)
class UniversityAdmissionCriteriaAdmin(admin.ModelAdmin):
    list_display = ['university', 'department', 'admission_type', 'year', 'created_at']
    list_filter = ['university', 'admission_type', 'year', 'created_at']
    search_fields = ['university__name', 'department']
    ordering = ['-year', 'university', 'department']
