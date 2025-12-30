from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Document, DocumentVersion
from .serializers import (
    DocumentSerializer,
    DocumentListSerializer,
    DocumentUploadSerializer,
    DocumentVersionSerializer
)


@extend_schema_view(
    list=extend_schema(tags=['Documents']),
    retrieve=extend_schema(tags=['Documents']),
    create=extend_schema(tags=['Documents']),
    update=extend_schema(tags=['Documents']),
    partial_update=extend_schema(tags=['Documents']),
    destroy=extend_schema(tags=['Documents']),
    versions=extend_schema(tags=['Documents']),
    add_version=extend_schema(tags=['Documents']),
)
class DocumentViewSet(viewsets.ModelViewSet):
    """서류 ViewSet"""
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'document_type', 'status']
    search_fields = ['title', 'student__name']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentListSerializer
        elif self.action in ['create', 'upload']:
            return DocumentUploadSerializer
        return DocumentSerializer

    def perform_create(self, serializer):
        """서류 생성 시 업로더 자동 설정"""
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=['post'])
    def upload_version(self, request, pk=None):
        """서류 새 버전 업로드"""
        document = self.get_object()

        # 최신 버전 번호 가져오기
        last_version = document.versions.first()
        version_number = (last_version.version_number + 1) if last_version else 1

        serializer = DocumentVersionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                document=document,
                version_number=version_number,
                created_by=request.user
            )
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """서류의 모든 버전 조회"""
        document = self.get_object()
        versions = document.versions.all()
        serializer = DocumentVersionSerializer(versions, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def process_ocr(self, request, pk=None):
        """OCR 처리 요청 (Celery 태스크)"""
        document = self.get_object()

        # TODO: Celery 태스크로 OCR 처리
        # from apps.documents.tasks import process_document_ocr
        # process_document_ocr.delay(document.id)

        document.status = 'PROCESSING'
        document.save()

        return Response({
            'success': True,
            'message': 'OCR 처리가 시작되었습니다.',
            'data': {'document_id': document.id, 'status': document.status}
        })

    @action(detail=True, methods=['post'])
    def analyze_ai(self, request, pk=None):
        """AI 분석 요청 (Celery 태스크)"""
        document = self.get_object()

        # TODO: Celery 태스크로 AI 분석
        # from apps.documents.tasks import analyze_document_ai
        # analyze_document_ai.delay(document.id)

        return Response({
            'success': True,
            'message': 'AI 분석이 시작되었습니다.',
            'data': {'document_id': document.id}
        })


@extend_schema_view(
    list=extend_schema(tags=['Documents']),
    retrieve=extend_schema(tags=['Documents']),
)
class DocumentVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """서류 버전 ViewSet (읽기 전용)"""
    queryset = DocumentVersion.objects.all()
    serializer_class = DocumentVersionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document']
