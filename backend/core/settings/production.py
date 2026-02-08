"""
Django production settings for petshop.
Use: DJANGO_SETTINGS_MODULE=core.settings.production
"""
import os
from .base import *
from decouple import config

DEBUG = False

# Garantir MEDIA_ROOT absoluto para Docker/volume
MEDIA_ROOT = os.path.abspath(str(BASE_DIR / 'media'))

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# Quando atrás de proxy (nginx) que termina SSL
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Trusted origins (scheme + domain) para CSRF
_csrf_origins = config('CSRF_TRUSTED_ORIGINS', default='', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])
CSRF_TRUSTED_ORIGINS = _csrf_origins

# CORS: permite a origem do frontend
_cors_origins = config('CORS_ALLOWED_ORIGINS', default='', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])
if _cors_origins:
    CORS_ALLOWED_ORIGINS = _cors_origins
else:
    # fallback: usa FRONTEND_URL
    _frontend = config('FRONTEND_URL', default='').rstrip('/')
    if _frontend:
        CORS_ALLOWED_ORIGINS = [_frontend]

CORS_ALLOW_CREDENTIALS = True

# WhiteNoise para arquivos estáticos (após SecurityMiddleware)
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
        'OPTIONS': {
            'location': str(BASE_DIR / 'media'),
        },
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
