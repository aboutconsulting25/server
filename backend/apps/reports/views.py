from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import ConsultationReport, ConsultationSession
from .serializers import (
    ConsultationReportSerializer,
    ConsultationReportListSerializer,
    ConsultationReportCreateSerializer,
    ConsultationSessionSerializer,
    ConsultationSessionListSerializer
)
from .ai_module import (
    get_mock_saenggibu_analysis,
    get_mock_grade_analysis,
    get_mock_comprehensive_analysis
)


@extend_schema_view(
    list=extend_schema(tags=['Reports']),
    retrieve=extend_schema(tags=['Reports']),
    create=extend_schema(tags=['Reports']),
    update=extend_schema(tags=['Reports']),
    partial_update=extend_schema(tags=['Reports']),
    destroy=extend_schema(tags=['Reports']),
    send=extend_schema(tags=['Reports']),
)
class ConsultationReportViewSet(viewsets.ModelViewSet):
    """컨설팅 리포트 ViewSet"""
    queryset = ConsultationReport.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'consultant', 'report_type', 'status']
    search_fields = ['title', 'student__name', 'consultant__name']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ConsultationReportListSerializer
        elif self.action == 'create':
            return ConsultationReportCreateSerializer
        return ConsultationReportSerializer

    @action(detail=True, methods=['post'])
    def send_report(self, request, pk=None):
        """리포트 전송"""
        report = self.get_object()

        if report.status != 'COMPLETED':
            return Response({
                'success': False,
                'error': '완료된 리포트만 전송할 수 있습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        report.status = 'SENT'
        report.sent_at = timezone.now()
        report.save()

        # TODO: 실제 전송 로직 (이메일, SMS 등)

        return Response({
            'success': True,
            'message': '리포트가 전송되었습니다.',
            'data': ConsultationReportSerializer(report).data
        })

    @action(detail=True, methods=['post'])
    def generate_ai_insights(self, request, pk=None):
        """AI 인사이트 생성"""
        report = self.get_object()

        # TODO: Celery 태스크로 AI 인사이트 생성
        # from apps.reports.tasks import generate_report_ai_insights
        # generate_report_ai_insights.delay(report.id)

        return Response({
            'success': True,
            'message': 'AI 인사이트 생성이 시작되었습니다.',
            'data': {'report_id': report.id}
        })

    @action(detail=False, methods=['get'])
    def student_reports(self, request):
        """특정 학생의 모든 리포트 조회"""
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response({
                'success': False,
                'error': 'student_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        reports = self.queryset.filter(student_id=student_id)
        serializer = ConsultationReportListSerializer(reports, many=True)

        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'total': reports.count()
            }
        })

    @action(detail=True, methods=['get'], url_path='comprehensive-analysis')
    def get_comprehensive_analysis(self, request, pk=None):
        """
        종합 분석 결과 조회 (프론트엔드용)

        GET /api/v1/reports/{report_id}/comprehensive-analysis/

        - AI 모듈의 종합분석 결과를 반환
        - university_analysis (수시카드)와 ai_insights.종합분석 통합
        """
        report = self.get_object()

        if not report.ai_insights.get('종합분석'):
            return Response({
                'success': False,
                'message': '종합 분석 결과가 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'success': True,
            'data': {
                'report_id': str(report.id),
                'student_id': str(report.student.id),
                'created_at': report.created_at,
                '종합분석': {
                    **report.ai_insights.get('종합분석', {}),
                    '수시카드': report.university_analysis
                }
            }
        })

    @action(detail=True, methods=['post'], url_path='generate-mock-analysis')
    @extend_schema(
        tags=['Reports'],
        summary='목업 분석 데이터 생성 (테스트용)',
        description='AI 모듈 연결 전 프론트엔드 개발을 위한 목업 데이터 생성'
    )
    def generate_mock_analysis(self, request, pk=None):
        """
        목업 분석 데이터 생성 (테스트용)

        POST /api/v1/reports/{report_id}/generate-mock-analysis/

        TODO: 실제 AI 모듈 연결 후 이 엔드포인트는 제거
        """
        report = self.get_object()

        # 목업 데이터 생성
        mock_grade_analysis = get_mock_grade_analysis()
        mock_comprehensive = get_mock_comprehensive_analysis()

        # 리포트에 저장
        report.ai_insights = {
            '성적분석': mock_grade_analysis,
            '종합분석': mock_comprehensive
        }
        report.university_analysis = mock_comprehensive['수시카드']
        report.status = 'COMPLETED'
        report.save()

        return Response({
            'success': True,
            'message': '목업 분석 데이터가 생성되었습니다.',
            'data': {
                'report_id': str(report.id),
                'status': report.status
            }
        })


@extend_schema_view(
    list=extend_schema(tags=['Reports']),
    retrieve=extend_schema(tags=['Reports']),
    create=extend_schema(tags=['Reports']),
    update=extend_schema(tags=['Reports']),
    partial_update=extend_schema(tags=['Reports']),
    destroy=extend_schema(tags=['Reports']),
    upcoming_sessions=extend_schema(tags=['Reports']),
    student_sessions=extend_schema(tags=['Reports']),
)
class ConsultationSessionViewSet(viewsets.ModelViewSet):
    """상담 세션 ViewSet"""
    queryset = ConsultationSession.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'consultant', 'session_type']
    search_fields = ['student__name', 'consultant__name', 'notes']
    ordering_fields = ['session_date', 'created_at']
    ordering = ['-session_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return ConsultationSessionListSerializer
        return ConsultationSessionSerializer

    @action(detail=False, methods=['get'])
    def upcoming_sessions(self, request):
        """다가오는 상담 세션 조회"""
        now = timezone.now()
        consultant_id = request.query_params.get('consultant_id')

        sessions = self.queryset.filter(session_date__gte=now)
        if consultant_id:
            sessions = sessions.filter(consultant_id=consultant_id)

        sessions = sessions.order_by('session_date')[:10]
        serializer = ConsultationSessionSerializer(sessions, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def student_sessions(self, request):
        """특정 학생의 상담 이력 조회"""
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response({
                'success': False,
                'error': 'student_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        sessions = self.queryset.filter(student_id=student_id)
        serializer = ConsultationSessionListSerializer(sessions, many=True)

        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'total': sessions.count()
            }
        })
