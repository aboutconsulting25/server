from rest_framework import serializers
from .models import Document, DocumentVersion
from apps.students.serializers import StudentListSerializer


class DocumentVersionSerializer(serializers.ModelSerializer):
    """서류 버전 시리얼라이저"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = DocumentVersion
        fields = [
            'id', 'document', 'version_number', 'file', 'file_size',
            'changes_description', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DocumentSerializer(serializers.ModelSerializer):
    """서류 시리얼라이저"""
    student_detail = StudentListSerializer(source='student', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    versions = DocumentVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'student', 'student_detail', 'document_type', 'title',
            'file', 'file_size', 'mime_type', 'status',
            'ocr_text', 'ai_analysis', 'uploaded_by', 'uploaded_by_name',
            'notes', 'versions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'file_size', 'mime_type', 'status', 'ocr_text', 'ai_analysis', 'created_at', 'updated_at']


class DocumentListSerializer(serializers.ModelSerializer):
    """서류 목록용 간단한 시리얼라이저"""
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'student', 'student_name', 'document_type',
            'title', 'status', 'created_at'
        ]
        read_only_fields = ['id']


class DocumentUploadSerializer(serializers.ModelSerializer):
    """서류 업로드용 시리얼라이저"""

    class Meta:
        model = Document
        fields = [
            'student', 'document_type', 'title', 'file', 'notes'
        ]

    def create(self, validated_data):
        # 파일 사이즈 자동 계산
        file = validated_data.get('file')
        if file:
            validated_data['file_size'] = file.size
            validated_data['mime_type'] = file.content_type

        # 업로드한 사용자 설정
        request = self.context.get('request')
        if request and request.user:
            validated_data['uploaded_by'] = request.user

        return super().create(validated_data)
