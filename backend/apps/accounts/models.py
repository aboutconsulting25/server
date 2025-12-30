import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, code, password=None, **extra_fields):
        if not code:
            raise ValueError('Users must have a code')

        user = self.model(code=code, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, code, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'SUPER_ADMIN')

        return self.create_user(code, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('SUPER_ADMIN', '대표 컨설턴트'),
        ('CONSULTANT', '일반 컨설턴트'),
        ('SCHOOL_ADMIN', '학원 관리자'),
        ('SALES', '영업 사원'),
        ('SPECIAL', '특수 권한'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=255, unique=True, verbose_name='로그인 코드')
    username = models.CharField(max_length=150, verbose_name='사용자명')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CONSULTANT')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'code'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = '사용자'
        verbose_name_plural = '사용자'

    def __str__(self):
        return f"{self.username} ({self.code})"
