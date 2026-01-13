from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import HighSchool, University, UniversityAdmissionCriteria
from .serializers import (
    HighSchoolSerializer, HighSchoolListSerializer,
    UniversitySerializer, UniversityListSerializer,
    UniversityAdmissionCriteriaSerializer
)


@extend_schema_view(
    list=extend_schema(tags=['Schools'], exclude=True),
    retrieve=extend_schema(tags=['Schools'], exclude=True),
    create=extend_schema(tags=['Schools'], exclude=True),
    update=extend_schema(tags=['Schools'], exclude=True),
    partial_update=extend_schema(tags=['Schools'], exclude=True),
    destroy=extend_schema(tags=['Schools'], exclude=True),
)
class HighSchoolViewSet(viewsets.ModelViewSet):
    """고등학교 ViewSet"""
    queryset = HighSchool.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['region', 'school_type']
    search_fields = ['name', 'region']
    ordering_fields = ['name', 'region', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return HighSchoolListSerializer
        return HighSchoolSerializer


@extend_schema_view(
    list=extend_schema(tags=['Schools'], exclude=True),
    retrieve=extend_schema(tags=['Schools'], exclude=True),
    create=extend_schema(tags=['Schools'], exclude=True),
    update=extend_schema(tags=['Schools'], exclude=True),
    partial_update=extend_schema(tags=['Schools'], exclude=True),
    destroy=extend_schema(tags=['Schools'], exclude=True),
    admission_criteria=extend_schema(tags=['Schools'], exclude=True),
)
class UniversityViewSet(viewsets.ModelViewSet):
    """대학 ViewSet"""
    queryset = University.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['region', 'university_type']
    search_fields = ['name', 'region']
    ordering_fields = ['name', 'ranking', 'created_at']
    ordering = ['ranking']

    def get_serializer_class(self):
        if self.action == 'list':
            return UniversityListSerializer
        return UniversitySerializer

    @action(detail=True, methods=['get'])
    def admission_criteria(self, request, pk=None):
        """특정 대학의 입학 기준 조회"""
        university = self.get_object()
        criteria = university.admission_criteria.all()
        serializer = UniversityAdmissionCriteriaSerializer(criteria, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })


@extend_schema_view(
    list=extend_schema(tags=['Schools'], exclude=True),
    retrieve=extend_schema(tags=['Schools'], exclude=True),
    create=extend_schema(tags=['Schools'], exclude=True),
    update=extend_schema(tags=['Schools'], exclude=True),
    partial_update=extend_schema(tags=['Schools'], exclude=True),
    destroy=extend_schema(tags=['Schools'], exclude=True),
)
class UniversityAdmissionCriteriaViewSet(viewsets.ModelViewSet):
    """대학 입학 기준 ViewSet"""
    queryset = UniversityAdmissionCriteria.objects.all()
    serializer_class = UniversityAdmissionCriteriaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['university', 'department', 'admission_type', 'year']
    search_fields = ['department', 'admission_type']
