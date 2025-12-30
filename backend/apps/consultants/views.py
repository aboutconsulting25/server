from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Consultant
from .serializers import (
    ConsultantSerializer,
    ConsultantListSerializer,
    ConsultantCreateSerializer
)


@extend_schema_view(
    list=extend_schema(tags=['Consultants']),
    retrieve=extend_schema(tags=['Consultants']),
    create=extend_schema(tags=['Consultants']),
    update=extend_schema(tags=['Consultants']),
    partial_update=extend_schema(tags=['Consultants']),
    destroy=extend_schema(tags=['Consultants']),
    students=extend_schema(tags=['Consultants']),
)
class ConsultantViewSet(viewsets.ModelViewSet):
    """컨설턴트 ViewSet"""
    queryset = Consultant.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization']
    search_fields = ['name', 'specialization']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ConsultantListSerializer
        elif self.action == 'create':
            return ConsultantCreateSerializer
        return ConsultantSerializer

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """특정 컨설턴트의 담당 학생 목록"""
        consultant = self.get_object()
        students = consultant.students.filter(status='ACTIVE')

        from apps.students.serializers import StudentListSerializer
        serializer = StudentListSerializer(students, many=True)

        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {
                'total': students.count(),
                'max_students': consultant.max_students
            }
        })

    @action(detail=True, methods=['get'])
    def workload(self, request, pk=None):
        """컨설턴트 업무량 조회"""
        consultant = self.get_object()
        current_students = consultant.current_students
        max_students = consultant.max_students

        return Response({
            'success': True,
            'data': {
                'consultant_id': consultant.id,
                'consultant_name': consultant.name,
                'current_students': current_students,
                'max_students': max_students,
                'capacity_percentage': round((current_students / max_students * 100), 2) if max_students > 0 else 0,
                'available_slots': max_students - current_students
            }
        })
