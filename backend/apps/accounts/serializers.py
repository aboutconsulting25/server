from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'code', 'username', 'role', 'is_active', 'created_at')
        read_only_fields = ('id', 'code', 'created_at')


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'code'

    def validate(self, attrs):
        # code로 인증
        data = super().validate(attrs)

        # 사용자 정보 추가
        data['user'] = UserSerializer(self.user).data

        return data
