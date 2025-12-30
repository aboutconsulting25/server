from rest_framework import serializers
from .models import Student, StudentDesiredUniversity
from apps.schools.serializers import HighSchoolListSerializer, UniversityListSerializer
from apps.consultants.serializers import ConsultantListSerializer


class StudentDesiredUniversitySerializer(serializers.ModelSerializer):
    """학생 지망 대학 시리얼라이저"""
    university_detail = UniversityListSerializer(source='university', read_only=True)

    class Meta:
        model = StudentDesiredUniversity
        fields = [
            'id', 'student', 'university', 'university_detail',
            'department', 'priority', 'admission_type', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentSerializer(serializers.ModelSerializer):
    """학생 시리얼라이저"""
    high_school_detail = HighSchoolListSerializer(source='high_school', read_only=True)
    consultant_detail = ConsultantListSerializer(source='consultant', read_only=True)
    desired_universities = StudentDesiredUniversitySerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'name', 'student_code', 'high_school', 'high_school_detail',
            'grade', 'phone', 'parent_phone', 'consultant', 'consultant_detail',
            'status', 'notes', 'desired_universities',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentListSerializer(serializers.ModelSerializer):
    """학생 목록용 간단한 시리얼라이저"""
    high_school_name = serializers.CharField(source='high_school.name', read_only=True)
    consultant_name = serializers.CharField(source='consultant.name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'name', 'student_code', 'high_school_name',
            'grade', 'consultant_name', 'status'
        ]
        read_only_fields = ['id']


class StudentCreateSerializer(serializers.ModelSerializer):
    """학생 생성용 시리얼라이저"""

    class Meta:
        model = Student
        fields = [
            'name', 'student_code', 'high_school', 'grade',
            'phone', 'parent_phone', 'consultant', 'status', 'notes'
        ]

    def validate_student_code(self, value):
        """학생 코드 중복 체크"""
        if Student.objects.filter(student_code=value).exists():
            raise serializers.ValidationError("이미 존재하는 학생 코드입니다.")
        return value
