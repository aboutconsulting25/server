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
from .utils import convert_9_to_5, convert_5_to_9


@extend_schema_view(
    list=extend_schema(tags=['Grades']),
    retrieve=extend_schema(tags=['Grades']),
    create=extend_schema(tags=['Grades']),
    update=extend_schema(tags=['Grades']),
    partial_update=extend_schema(tags=['Grades']),
    destroy=extend_schema(tags=['Grades']),
    subject_grades=extend_schema(tags=['Grades']),
    add_subject_grade=extend_schema(tags=['Grades']),
    convert_grade=extend_schema(tags=['Grades']),
    student_grade_summary=extend_schema(tags=['Grades']),
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

    @action(detail=False, methods=['post'])
    def convert_grade(self, request):
        """등급 변환 API (9등급제 ↔ 5등급제)

        Parameters:
            - grade (float): 변환할 등급
            - from_system (str): 원본 등급 시스템 ('9' or '5')
            - to_system (str): 대상 등급 시스템 ('9' or '5')

        Returns:
            - converted_grade (float): 변환된 등급
            - original_grade (float): 원본 등급
            - from_system (str): 원본 시스템
            - to_system (str): 대상 시스템
        """
        grade = request.data.get('grade')
        from_system = request.data.get('from_system', '9')
        to_system = request.data.get('to_system', '5')

        # 입력 검증
        if grade is None:
            return Response({
                'success': False,
                'error': 'grade parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            grade = float(grade)
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'grade must be a valid number'
            }, status=status.HTTP_400_BAD_REQUEST)

        if from_system not in ['9', '5'] or to_system not in ['9', '5']:
            return Response({
                'success': False,
                'error': 'from_system and to_system must be either "9" or "5"'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 같은 시스템 간 변환은 그대로 반환
        if from_system == to_system:
            return Response({
                'success': True,
                'data': {
                    'original_grade': grade,
                    'converted_grade': grade,
                    'from_system': from_system,
                    'to_system': to_system
                }
            })

        # 등급 변환
        try:
            if from_system == '9' and to_system == '5':
                converted = convert_9_to_5(grade)
            else:  # from_system == '5' and to_system == '9'
                converted = convert_5_to_9(grade)

            return Response({
                'success': True,
                'data': {
                    'original_grade': grade,
                    'converted_grade': converted,
                    'from_system': from_system,
                    'to_system': to_system
                }
            })
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
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
