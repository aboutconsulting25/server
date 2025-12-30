import uuid
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User


class UserModelTest(TestCase):
    """User 모델 테스트"""

    def setUp(self):
        self.code = str(uuid.uuid4())
        self.user_data = {
            'code': self.code,
            'username': '테스트사용자',
            'password': 'testpass123',
            'role': 'CONSULTANT'
        }

    def test_create_user(self):
        """일반 사용자 생성 테스트"""
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.code, self.code)
        self.assertEqual(user.username, '테스트사용자')
        self.assertEqual(user.role, 'CONSULTANT')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password('testpass123'))

    def test_create_superuser(self):
        """슈퍼유저 생성 테스트"""
        user = User.objects.create_superuser(
            code=self.code,
            username='관리자',
            password='admin123'
        )

        self.assertEqual(user.role, 'SUPER_ADMIN')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_string_representation(self):
        """User 모델 __str__ 테스트"""
        user = User.objects.create_user(**self.user_data)
        expected = f"테스트사용자 ({self.code})"
        self.assertEqual(str(user), expected)

    def test_create_user_without_code(self):
        """코드 없이 사용자 생성 시 에러 테스트"""
        with self.assertRaises(ValueError):
            User.objects.create_user(code='', username='테스트', password='test123')


class AuthenticationAPITest(APITestCase):
    """인증 API 테스트"""

    def setUp(self):
        self.client = APIClient()
        self.code = str(uuid.uuid4())
        self.password = 'testpass123'

        # 테스트 사용자 생성
        self.user = User.objects.create_user(
            code=self.code,
            username='김컨설턴트',
            password=self.password,
            role='CONSULTANT'
        )

        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.me_url = reverse('user_me')

    def test_login_success(self):
        """로그인 성공 테스트"""
        data = {
            'code': self.code,
            'password': self.password
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

        # 사용자 정보 확인
        user_data = response.data['user']
        self.assertEqual(user_data['code'], self.code)
        self.assertEqual(user_data['username'], '김컨설턴트')
        self.assertEqual(user_data['role'], 'CONSULTANT')

    def test_login_with_wrong_password(self):
        """잘못된 비밀번호로 로그인 실패 테스트"""
        data = {
            'code': self.code,
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_wrong_code(self):
        """존재하지 않는 코드로 로그인 실패 테스트"""
        data = {
            'code': str(uuid.uuid4()),
            'password': self.password
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_inactive_user(self):
        """비활성화된 사용자 로그인 실패 테스트"""
        # 사용자 비활성화
        self.user.is_active = False
        self.user.save()

        data = {
            'code': self.code,
            'password': self.password
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """토큰 갱신 테스트"""
        # 먼저 로그인하여 refresh token 획득
        login_data = {
            'code': self.code,
            'password': self.password
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']

        # 토큰 갱신
        refresh_data = {
            'refresh': refresh_token
        }
        response = self.client.post(self.refresh_url, refresh_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_get_current_user_info(self):
        """현재 사용자 정보 조회 테스트"""
        # 로그인하여 access token 획득
        login_data = {
            'code': self.code,
            'password': self.password
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['access']

        # 인증 헤더 설정
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 사용자 정보 조회
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)

        user_data = response.data['data']
        self.assertEqual(user_data['code'], self.code)
        self.assertEqual(user_data['username'], '김컨설턴트')
        self.assertEqual(user_data['role'], 'CONSULTANT')

    def test_get_user_info_without_authentication(self):
        """인증 없이 사용자 정보 조회 실패 테스트"""
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_info_with_invalid_token(self):
        """잘못된 토큰으로 사용자 정보 조회 실패 테스트"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserRoleTest(APITestCase):
    """사용자 역할별 테스트"""

    def setUp(self):
        self.client = APIClient()

        # 각 역할별 사용자 생성
        self.super_admin = User.objects.create_user(
            code=str(uuid.uuid4()),
            username='대표컨설턴트',
            password='test123',
            role='SUPER_ADMIN',
            is_staff=True,
            is_superuser=True
        )

        self.consultant = User.objects.create_user(
            code=str(uuid.uuid4()),
            username='일반컨설턴트',
            password='test123',
            role='CONSULTANT'
        )

        self.school_admin = User.objects.create_user(
            code=str(uuid.uuid4()),
            username='학원관리자',
            password='test123',
            role='SCHOOL_ADMIN'
        )

    def test_super_admin_role(self):
        """SUPER_ADMIN 역할 테스트"""
        self.assertEqual(self.super_admin.role, 'SUPER_ADMIN')
        self.assertTrue(self.super_admin.is_staff)
        self.assertTrue(self.super_admin.is_superuser)

    def test_consultant_role(self):
        """CONSULTANT 역할 테스트"""
        self.assertEqual(self.consultant.role, 'CONSULTANT')
        self.assertFalse(self.consultant.is_staff)
        self.assertFalse(self.consultant.is_superuser)

    def test_school_admin_role(self):
        """SCHOOL_ADMIN 역할 테스트"""
        self.assertEqual(self.school_admin.role, 'SCHOOL_ADMIN')
        self.assertFalse(self.school_admin.is_staff)
