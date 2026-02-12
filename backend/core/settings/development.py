from .base import *

DEBUG = True

# Em desenvolvimento: executa tarefas Celery de forma síncrona (sem Redis)
CELERY_TASK_ALWAYS_EAGER = True

# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Development database (can use SQLite for easy setup)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Override with PostgreSQL if configured
if config('USE_POSTGRES', default=False, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='petshop_db'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='postgres'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
