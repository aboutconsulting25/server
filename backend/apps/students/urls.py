from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.StudentViewSet, basename='student')
router.register(r'desired-universities', views.StudentDesiredUniversityViewSet, basename='desired-university')

urlpatterns = [
    path('', include(router.urls)),
]
