from .base import *

DEBUG = True

# Django Debug Toolbar (only if installed)
try:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    INTERNAL_IPS = ['127.0.0.1']
except ImportError:
    pass

# Email Backend - Console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# S3 사용 안 함 (로컬 파일 시스템)
USE_S3 = False

# CORS - 개발 환경에서는 모든 origin 허용
CORS_ALLOW_ALL_ORIGINS = True
