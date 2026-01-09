from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from apps.students.mvp_views import register_saenggibu_onestop

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # MVP 원포인트 API
    path('api/v1/mvp/register-saenggibu/', register_saenggibu_onestop, name='mvp-register-saenggibu'),

    # API v1
    # 로그인 API 비활성화 (MVP용) - 추후 재활성화 예정
    # path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/students/', include('apps.students.urls')),
    path('api/v1/consultants/', include('apps.consultants.urls')),
    path('api/v1/documents/', include('apps.documents.urls')),
    path('api/v1/grades/', include('apps.grades.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/schools/', include('apps.schools.urls')),
]

# Media files (개발 환경)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Debug Toolbar (개발 환경)
if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
