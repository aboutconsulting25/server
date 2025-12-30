from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'consultation-reports', views.ConsultationReportViewSet, basename='consultation-report')
router.register(r'consultation-sessions', views.ConsultationSessionViewSet, basename='consultation-session')

urlpatterns = [
    path('', include(router.urls)),
]
