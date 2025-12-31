from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Document, DocumentAnalysis
from .serializers import (
    DocumentSerializer,
    DocumentListSerializer,
    DocumentUploadSerializer,
    DocumentAnalysisSerializer
)


@extend_schema_view(
    list=extend_schema(tags=['Documents'], summary='문서 목록 조회'),
    retrieve=extend_schema(tags=['Documents'], summary='문서 상세 조회'),
    create=extend_schema(tags=['Documents'], summary='문서 업로드'),
    destroy=extend_schema(tags=['Documents'], summary='문서 삭제'),
)
class DocumentViewSet(viewsets.ModelViewSet):
    """
    생기부/성적표 문서 관리 ViewSet

    - 같은 학생의 새 문서 업로드 시 자동으로 버전 증가
    - is_latest로 최신 버전 자동 표시
    """
    queryset = Document.objects.select_related('student', 'uploaded_by').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'document_type', 'is_latest', 'status']
    search_fields = ['title', 'student__name']
    ordering_fields = ['created_at', 'updated_at', 'version']
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'delete']  # PUT, PATCH 제거

    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentListSerializer
        elif self.action == 'create':
            return DocumentUploadSerializer
        return DocumentSerializer

    def perform_create(self, serializer):
        """서류 생성 시 업로더 자동 설정"""
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='analyze')
    @extend_schema(
        tags=['Documents'],
        summary='문서 분석 시작',
        description='OCR 및 AI 분석을 시작합니다. Celery를 통해 비동기로 처리됩니다.'
    )
    def start_analysis(self, request, pk=None):
        """
        문서 분석 시작
        - OCR 처리
        - AI 분석
        """
        document = self.get_object()

        # 이미 처리 중인지 확인
        if document.status == 'PROCESSING':
            return Response({
                'success': False,
                'message': '이미 처리 중인 문서입니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # DocumentAnalysis 생성
        analysis = DocumentAnalysis.objects.create(
            document=document,
            student=document.student,
            status='PENDING'
        )

        # 문서 상태 업데이트
        document.status = 'PROCESSING'
        document.save()

        # TODO: Celery 태스크 실행
        # from apps.documents.tasks import process_document_analysis
        # process_document_analysis.delay(str(analysis.id))

        return Response({
            'success': True,
            'message': '분석이 시작되었습니다.',
            'data': {
                'document_id': str(document.id),
                'analysis_id': str(analysis.id),
                'status': analysis.status
            }
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['get'], url_path='analyses')
    @extend_schema(
        tags=['Documents'],
        summary='문서의 모든 분석 이력 조회'
    )
    def get_analyses(self, request, pk=None):
        """문서의 모든 분석 이력 조회"""
        document = self.get_object()
        analyses = document.analyses.all()
        serializer = DocumentAnalysisSerializer(analyses, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })


@extend_schema_view(
    list=extend_schema(tags=['Documents'], summary='분석 이력 목록'),
    retrieve=extend_schema(tags=['Documents'], summary='분석 상세 조회'),
)
class DocumentAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    문서 분석 이력 ViewSet (읽기 전용)
    """
    queryset = DocumentAnalysis.objects.select_related(
        'document', 'student'
    ).all()
    serializer_class = DocumentAnalysisSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document', 'student', 'status']


# 기존 DocumentVersion 관련 코드 (주석 처리)
# from .models import DocumentVersion
# from .serializers import DocumentVersionSerializer
#
# @extend_schema_view(
#     list=extend_schema(tags=['Documents']),
#     retrieve=extend_schema(tags=['Documents']),
# )
# class DocumentVersionViewSet(viewsets.ReadOnlyModelViewSet):
#     """서류 버전 ViewSet (읽기 전용)"""
#     queryset = DocumentVersion.objects.all()
#     serializer_class = DocumentVersionSerializer
#     permission_classes = [IsAuthenticated]
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['document']
