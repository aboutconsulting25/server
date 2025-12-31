from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'documents', views.DocumentViewSet, basename='document')
router.register(r'analyses', views.DocumentAnalysisViewSet, basename='analysis')

urlpatterns = [
    path('', include(router.urls)),
]

# 기존 DocumentVersion 관련 코드 (주석 처리)
# router.register(r'versions', views.DocumentVersionViewSet, basename='document-version')
