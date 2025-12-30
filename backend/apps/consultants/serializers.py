from rest_framework import serializers
from .models import Consultant
from apps.accounts.serializers import UserSerializer


class ConsultantSerializer(serializers.ModelSerializer):
    """컨설턴트 시리얼라이저"""
    user = UserSerializer(read_only=True)
    current_students_count = serializers.IntegerField(source='current_students', read_only=True)

    class Meta:
        model = Consultant
        fields = [
            'id', 'user', 'name', 'phone', 'specialization',
            'max_students', 'current_students_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ConsultantListSerializer(serializers.ModelSerializer):
    """컨설턴트 목록용 간단한 시리얼라이저"""
    current_students_count = serializers.IntegerField(source='current_students', read_only=True)

    class Meta:
        model = Consultant
        fields = [
            'id', 'name', 'specialization',
            'max_students', 'current_students_count'
        ]
        read_only_fields = ['id']


class ConsultantCreateSerializer(serializers.ModelSerializer):
    """컨설턴트 생성용 시리얼라이저"""
    user_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Consultant
        fields = [
            'user_id', 'name', 'phone', 'specialization', 'max_students'
        ]

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        consultant = Consultant.objects.create(
            user_id=user_id,
            **validated_data
        )
        return consultant
