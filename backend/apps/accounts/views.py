from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import CustomTokenObtainPairSerializer, UserSerializer


@extend_schema(tags=['Auth'])
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(tags=['Auth'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_me(request):
    """현재 사용자 정보 조회"""
    serializer = UserSerializer(request.user)
    return Response({
        'success': True,
        'data': serializer.data
    })
