from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Grade, SubjectGrade
from .serializers import (
    GradeSerializer,
    GradeListSerializer,
    GradeCreateSerializer,
    SubjectGradeSerializer
)


@extend_schema_view(
    list=extend_schema(tags=['Grades']),
    retrieve=extend_schema(tags=['Grades']),
    create=extend_schema(tags=['Grades']),
    update=extend_schema(tags=['Grades']),
    partial_update=extend_schema(tags=['Grades']),
    destroy=extend_schema(tags=['Grades']),
    subjects=extend_schema(tags=['Grades']),
)
class GradeViewSet(viewsets.ModelViewSet):
    """성적 ViewSet"""
    queryset = Grade.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'semester', 'exam_type']
    search_fields = ['student__name']
    ordering_fields = ['semester', 'created_at']
    ordering = ['semester', 'exam_type']

    def get_serializer_class(self):
        if self.action == 'list':
            return GradeListSerializer
        elif self.action == 'create':
            return GradeCreateSerializer
        return GradeSerializer

    @action(detail=True, methods=['get'])
    def subject_grades(self, request, pk=None):
        """특정 성적의 과목별 성적 조회"""
        grade = self.get_object()
        subject_grades = grade.subject_grades.all()
        serializer = SubjectGradeSerializer(subject_grades, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def add_subject_grade(self, request, pk=None):
        """과목별 성적 추가"""
        grade = self.get_object()
        serializer = SubjectGradeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(grade=grade)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def student_grade_summary(self, request):
        """학생별 성적 요약"""
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response({
                'success': False,
                'error': 'student_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        grades = self.queryset.filter(student_id=student_id)
        serializer = GradeListSerializer(grades, many=True)

        # 평균 계산
        total_gpa = sum([g.gpa for g in grades if g.gpa])
        avg_gpa = total_gpa / len(grades) if grades else 0

        return Response({
            'success': True,
            'data': {
                'student_id': student_id,
                'grades': serializer.data,
                'summary': {
                    'total_records': grades.count(),
                    'average_gpa': round(avg_gpa, 2)
                }
            }
        })


@extend_schema_view(
    list=extend_schema(tags=['Grades']),
    retrieve=extend_schema(tags=['Grades']),
    create=extend_schema(tags=['Grades']),
    update=extend_schema(tags=['Grades']),
    partial_update=extend_schema(tags=['Grades']),
    destroy=extend_schema(tags=['Grades']),
)
class SubjectGradeViewSet(viewsets.ModelViewSet):
    """과목별 성적 ViewSet"""
    queryset = SubjectGrade.objects.all()
    serializer_class = SubjectGradeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['grade', 'subject_name']
    search_fields = ['subject_name']
