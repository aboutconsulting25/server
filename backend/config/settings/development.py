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
