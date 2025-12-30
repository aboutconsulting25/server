from rest_framework import serializers
from .models import ConsultationReport, ConsultationSession
from apps.students.serializers import StudentListSerializer
from apps.consultants.serializers import ConsultantListSerializer


class ConsultationReportSerializer(serializers.ModelSerializer):
    """컨설팅 리포트 시리얼라이저"""
    student_detail = StudentListSerializer(source='student', read_only=True)
    consultant_detail = ConsultantListSerializer(source='consultant', read_only=True)

    class Meta:
        model = ConsultationReport
        fields = [
            'id', 'student', 'student_detail', 'consultant', 'consultant_detail',
            'report_type', 'title', 'summary', 'content', 'current_status',
            'university_analysis', 'improvement_plan', 'action_items',
            'ai_insights', 'status', 'report_file', 'sent_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sent_at', 'created_at', 'updated_at']


class ConsultationReportListSerializer(serializers.ModelSerializer):
    """컨설팅 리포트 목록용 간단한 시리얼라이저"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    consultant_name = serializers.CharField(source='consultant.name', read_only=True)

    class Meta:
        model = ConsultationReport
        fields = [
            'id', 'student', 'student_name', 'consultant', 'consultant_name',
            'report_type', 'title', 'status', 'created_at'
        ]
        read_only_fields = ['id']


class ConsultationReportCreateSerializer(serializers.ModelSerializer):
    """컨설팅 리포트 생성용 시리얼라이저"""

    class Meta:
        model = ConsultationReport
        fields = [
            'student', 'consultant', 'report_type', 'title',
            'summary', 'content', 'current_status', 'university_analysis',
            'improvement_plan', 'action_items', 'ai_insights'
        ]


class ConsultationSessionSerializer(serializers.ModelSerializer):
    """상담 세션 시리얼라이저"""
    student_detail = StudentListSerializer(source='student', read_only=True)
    consultant_detail = ConsultantListSerializer(source='consultant', read_only=True)

    class Meta:
        model = ConsultationSession
        fields = [
            'id', 'student', 'student_detail', 'consultant', 'consultant_detail',
            'session_type', 'session_date', 'duration_minutes',
            'topics_discussed', 'notes', 'next_actions', 'next_session_date',
            'attachments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ConsultationSessionListSerializer(serializers.ModelSerializer):
    """상담 세션 목록용 간단한 시리얼라이저"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    consultant_name = serializers.CharField(source='consultant.name', read_only=True)

    class Meta:
        model = ConsultationSession
        fields = [
            'id', 'student', 'student_name', 'consultant', 'consultant_name',
            'session_type', 'session_date', 'duration_minutes'
        ]
        read_only_fields = ['id']
