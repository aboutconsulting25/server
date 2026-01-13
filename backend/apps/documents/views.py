from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Document, DocumentAnalysis
from .serializers import (
    DocumentSerializer,
    DocumentListSerializer,
    DocumentUploadSerializer,
    DocumentAnalysisSerializer
)
from apps.reports.ai_module import get_mock_saenggibu_analysis


@extend_schema_view(
    list=extend_schema(tags=['Documents'], summary='문서 목록 조회', exclude=True),
    retrieve=extend_schema(tags=['Documents'], summary='문서 상세 조회', exclude=True),
    create=extend_schema(tags=['Documents'], summary='문서 업로드', exclude=True),
    destroy=extend_schema(tags=['Documents'], summary='문서 삭제', exclude=True),
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
        description='OCR 및 AI 분석을 시작합니다. Celery를 통해 비동기로 처리됩니다.',
        exclude=True
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
        summary='문서의 모든 분석 이력 조회',
        exclude=True
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

    @action(detail=True, methods=['get'], url_path='latest-analysis')
    @extend_schema(
        tags=['Documents'],
        summary='문서의 최신 분석 결과 조회',
        description='생기부 분석 결과를 프론트엔드에서 사용할 수 있는 형태로 반환'
    )
    def get_latest_analysis(self, request, pk=None):
        """
        문서의 최신 완료된 분석 결과 조회
        - 프론트엔드가 사용할 생기부 분석 화면용 API
        """
        document = self.get_object()
        latest_analysis = document.analyses.filter(
            status='COMPLETED'
        ).order_by('-analysis_version').first()

        if not latest_analysis:
            return Response({
                'success': False,
                'message': '완료된 분석 결과가 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'success': True,
            'data': {
                'analysis_id': str(latest_analysis.id),
                'analysis_version': latest_analysis.analysis_version,
                'completed_at': latest_analysis.completed_at,
                '생기부_분석': latest_analysis.analysis_result
            }
        })

    @action(detail=True, methods=['patch'], url_path='update-analysis')
    @extend_schema(
        tags=['Documents'],
        summary='생기부 분석 결과 수정 (컨설턴트용)',
        description='컨설턴트가 AI 분석 결과를 검토 후 수정할 수 있는 API',
        exclude=True
    )
    def update_analysis_result(self, request, pk=None):
        """
        생기부 분석 결과 수정

        PATCH /api/v1/documents/{document_id}/update-analysis/

        - 최신 완료된 분석 결과를 수정
        - 전체 또는 일부 필드만 수정 가능
        """
        document = self.get_object()
        latest_analysis = document.analyses.filter(
            status='COMPLETED'
        ).order_by('-analysis_version').first()

        if not latest_analysis:
            return Response({
                'success': False,
                'message': '수정할 분석 결과가 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)

        # 기존 분석 결과와 병합
        updated_data = request.data.get('생기부_분석', {})
        if not updated_data:
            return Response({
                'success': False,
                'error': '생기부_분석 필드가 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Deep merge: 기존 데이터와 새 데이터 병합
        from copy import deepcopy
        merged_result = deepcopy(latest_analysis.analysis_result)

        def deep_update(source, updates):
            """중첩된 dict를 재귀적으로 업데이트"""
            for key, value in updates.items():
                if isinstance(value, dict) and key in source and isinstance(source[key], dict):
                    deep_update(source[key], value)
                else:
                    source[key] = value

        deep_update(merged_result, updated_data)

        # 새 버전으로 저장
        new_analysis = DocumentAnalysis.objects.create(
            document=document,
            student=document.student,
            status='COMPLETED',
            analysis_result=merged_result,
            started_at=latest_analysis.started_at,
            completed_at=timezone.now()
        )

        return Response({
            'success': True,
            'message': '분석 결과가 수정되었습니다.',
            'data': {
                'analysis_id': str(new_analysis.id),
                'analysis_version': new_analysis.analysis_version,
                'updated_fields': list(updated_data.keys())
            }
        })

    @action(detail=True, methods=['post'], url_path='generate-mock-analysis')
    @extend_schema(
        tags=['Documents'],
        summary='생기부 목업 분석 생성 (테스트용)',
        description='AI 모듈 연결 전 프론트엔드 개발을 위한 목업 데이터 생성',
        exclude=True
    )
    def generate_mock_analysis(self, request, pk=None):
        """
        생기부 목업 분석 데이터 생성 (테스트용)

        POST /api/v1/documents/{document_id}/generate-mock-analysis/

        TODO: 실제 AI 모듈 연결 후 이 엔드포인트는 제거
        """
        document = self.get_object()

        # 기존 미완료 분석 삭제 또는 완료 처리
        document.analyses.filter(status__in=['PENDING', 'PROCESSING']).delete()

        # 목업 분석 데이터 생성
        mock_analysis = get_mock_saenggibu_analysis()

        # DocumentAnalysis 생성
        analysis = DocumentAnalysis.objects.create(
            document=document,
            student=document.student,
            status='COMPLETED',
            analysis_result=mock_analysis,
            started_at=timezone.now(),
            completed_at=timezone.now()
        )

        # 문서 상태 업데이트
        document.status = 'COMPLETED'
        document.save()

        return Response({
            'success': True,
            'message': '목업 생기부 분석 데이터가 생성되었습니다.',
            'data': {
                'document_id': str(document.id),
                'analysis_id': str(analysis.id),
                'status': analysis.status
            }
        })


@extend_schema_view(
    list=extend_schema(tags=['Documents'], summary='분석 이력 목록', exclude=True),
    retrieve=extend_schema(tags=['Documents'], summary='분석 상세 조회', exclude=True),
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
