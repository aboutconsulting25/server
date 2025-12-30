from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'high-schools', views.HighSchoolViewSet, basename='highschool')
router.register(r'universities', views.UniversityViewSet, basename='university')
router.register(r'admission-criteria', views.UniversityAdmissionCriteriaViewSet, basename='admission-criteria')

urlpatterns = [
    path('', include(router.urls)),
]
