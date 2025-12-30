from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.DocumentViewSet, basename='document')
router.register(r'versions', views.DocumentVersionViewSet, basename='document-version')

urlpatterns = [
    path('', include(router.urls)),
]
