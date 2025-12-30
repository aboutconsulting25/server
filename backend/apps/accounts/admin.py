from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['code', 'username', 'role', 'is_active', 'is_staff', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['code', 'username']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('code', 'password')}),
        ('개인정보', {'fields': ('username', 'email')}),
        ('권한', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('중요한 날짜', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('code', 'username', 'password1', 'password2', 'role'),
        }),
    )

    readonly_fields = ['created_at', 'updated_at']
