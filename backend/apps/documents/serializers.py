from rest_framework import serializers
from .models import Document, DocumentAnalysis
from apps.students.serializers import StudentListSerializer


class DocumentAnalysisSerializer(serializers.ModelSerializer):
    """문서 분석 결과 시리얼라이저"""
    document_version = serializers.IntegerField(source='document.version', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = DocumentAnalysis
        fields = [
            'id', 'document', 'document_version', 'student', 'student_name',
            'analysis_version', 'status',
            'ocr_result', 'analysis_result', 'error_message',
            'started_at', 'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'analysis_version', 'started_at',
            'completed_at', 'created_at', 'updated_at'
        ]


class DocumentSerializer(serializers.ModelSerializer):
    """서류 상세 시리얼라이저"""
    student_detail = StudentListSerializer(source='student', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)

    # 최신 분석 결과만 포함
    latest_analysis = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'student', 'student_detail', 'document_type', 'title',
            'file', 'file_size', 'mime_type', 'status',
            'version', 'is_latest',
            'uploaded_by', 'uploaded_by_name',
            'notes', 'latest_analysis',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'mime_type', 'status', 'version',
            'created_at', 'updated_at'
        ]

    def get_latest_analysis(self, obj):
        """최신 분석 결과 가져오기"""
        latest = obj.analyses.filter(status='COMPLETED').order_by('-analysis_version').first()
        if latest:
            return DocumentAnalysisSerializer(latest).data
        return None


class DocumentListSerializer(serializers.ModelSerializer):
    """서류 목록용 간단한 시리얼라이저"""
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'student', 'student_name', 'document_type',
            'title', 'version', 'is_latest', 'status', 'created_at'
        ]
        read_only_fields = ['id']


class DocumentUploadSerializer(serializers.ModelSerializer):
    """서류 업로드용 시리얼라이저"""

    class Meta:
        model = Document
        fields = [
            'student', 'document_type', 'title', 'file', 'notes'
        ]

    def validate_file(self, value):
        """파일 검증"""
        # 파일 크기 체크 (10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("파일 크기는 10MB를 초과할 수 없습니다.")

        # MIME 타입 체크
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"허용되지 않는 파일 형식입니다. (허용: PDF, JPG, PNG)"
            )

        return value

    def create(self, validated_data):
        # 파일 정보 자동 설정
        file = validated_data.get('file')
        if file:
            validated_data['file_size'] = file.size
            validated_data['mime_type'] = file.content_type

        # 업로드한 사용자 설정
        request = self.context.get('request')
        if request and request.user:
            validated_data['uploaded_by'] = request.user

        return super().create(validated_data)


# 기존 DocumentVersion 관련 코드 (주석 처리)
# from .models import DocumentVersion
#
# class DocumentVersionSerializer(serializers.ModelSerializer):
#     """서류 버전 시리얼라이저"""
#     created_by_name = serializers.CharField(source='created_by.username', read_only=True)
#
#     class Meta:
#         model = DocumentVersion
#         fields = [
#             'id', 'document', 'version_number', 'file', 'file_size',
#             'changes_description', 'created_by', 'created_by_name', 'created_at'
#         ]
#         read_only_fields = ['id', 'created_at']
