from rest_framework import serializers
from .models import HighSchool, University, UniversityAdmissionCriteria


class HighSchoolSerializer(serializers.ModelSerializer):
    """고등학교 시리얼라이저"""

    class Meta:
        model = HighSchool
        fields = [
            'id', 'name', 'region', 'district', 'school_type', 'ranking',
            'statistics', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HighSchoolListSerializer(serializers.ModelSerializer):
    """고등학교 목록용 간단한 시리얼라이저"""

    class Meta:
        model = HighSchool
        fields = ['id', 'name', 'region', 'school_type']
        read_only_fields = ['id']


class UniversityAdmissionCriteriaSerializer(serializers.ModelSerializer):
    """대학 입학 기준 시리얼라이저"""

    class Meta:
        model = UniversityAdmissionCriteria
        fields = [
            'id', 'university', 'department', 'admission_type',
            'year', 'criteria', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UniversitySerializer(serializers.ModelSerializer):
    """대학 시리얼라이저"""
    admission_criteria = UniversityAdmissionCriteriaSerializer(many=True, read_only=True)

    class Meta:
        model = University
        fields = [
            'id', 'name', 'region', 'university_type', 'ranking',
            'metadata', 'admission_criteria',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UniversityListSerializer(serializers.ModelSerializer):
    """대학 목록용 간단한 시리얼라이저"""

    class Meta:
        model = University
        fields = ['id', 'name', 'region', 'university_type', 'ranking']
        read_only_fields = ['id']
