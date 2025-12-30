import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.accounts.models import User

# 테스트 사용자 생성
code = str(uuid.uuid4())
user = User.objects.create_user(
    code=code,
    username='테스트컨설턴트',
    password='test1234',
    role='CONSULTANT'
)

print(f"테스트 사용자 생성 완료!")
print(f"Code: {code}")
print(f"Password: test1234")
