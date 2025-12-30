from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Student, StudentDesiredUniversity
from .serializers import (
    StudentSerializer,
    StudentListSerializer,
    StudentCreateSerializer,
    StudentDesiredUniversitySerializer
)


@extend_schema_view(
    list=extend_schema(tags=['Students']),
    retrieve=extend_schema(tags=['Students']),
    create=extend_schema(tags=['Students']),
    update=extend_schema(tags=['Students']),
    partial_update=extend_schema(tags=['Students']),
    destroy=extend_schema(tags=['Students']),
    desired_universities=extend_schema(tags=['Students']),
    add_desired_university=extend_schema(tags=['Students']),
    grades=extend_schema(tags=['Students']),
    documents=extend_schema(tags=['Students']),
)
class StudentViewSet(viewsets.ModelViewSet):
    """학생 ViewSet"""
    queryset = Student.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['high_school', 'grade', 'consultant', 'status']
    search_fields = ['name', 'student_code']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return StudentListSerializer
        elif self.action == 'create':
            return StudentCreateSerializer
        return StudentSerializer

    @action(detail=True, methods=['get'])
    def desired_universities(self, request, pk=None):
        """학생의 지망 대학 목록"""
        student = self.get_object()
        desired = student.desired_universities.all()
        serializer = StudentDesiredUniversitySerializer(desired, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def add_desired_university(self, request, pk=None):
        """지망 대학 추가"""
        student = self.get_object()
        serializer = StudentDesiredUniversitySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(student=student)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def grades(self, request, pk=None):
        """학생의 성적 목록"""
        student = self.get_object()
        grades = student.grades.all()

        from apps.grades.serializers import GradeListSerializer
        serializer = GradeListSerializer(grades, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """학생의 서류 목록"""
        student = self.get_object()
        documents = student.documents.all()

        from apps.documents.serializers import DocumentListSerializer
        serializer = DocumentListSerializer(documents, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })


@extend_schema_view(
    list=extend_schema(tags=['Students']),
    retrieve=extend_schema(tags=['Students']),
    create=extend_schema(tags=['Students']),
    update=extend_schema(tags=['Students']),
    partial_update=extend_schema(tags=['Students']),
    destroy=extend_schema(tags=['Students']),
)
class StudentDesiredUniversityViewSet(viewsets.ModelViewSet):
    """학생 지망 대학 ViewSet"""
    queryset = StudentDesiredUniversity.objects.all()
    serializer_class = StudentDesiredUniversitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['student', 'university', 'priority']
    search_fields = ['department']
