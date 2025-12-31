"""
Base settings wrapper.

This project currently uses `Backend.settings` as the canonical Django settings
module (see `manage.py` and `Backend/settings.py`). The `config/settings/`
package is kept as an optional wrapper for environment-specific settings.

To avoid accidental imports of stale/unknown modules, re-export everything
from `Backend.settings` here. If you prefer to use `config.settings` as the
primary settings package, replace the import target accordingly.
"""

# Moved/normalized settings from Backend/settings.py into config/settings/base.py
# Adjust BASE_DIR so it points to project root (config/settings -> config -> project root).
from pathlib import Path
import os

# Try to import dotenv, but do not fail if it's not installed in the environment
try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - defensive for environments without python-dotenv
    def load_dotenv(*args, **kwargs):
        return None

# Load .env from project root if present
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Helper parsing
def _bool_env(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).lower() in ('1', 'true', 'yes', 'on')


def _list_env(value: str | None, default: list[str] | None = None) -> list[str]:
    if value is None:
        return default or []
    return [p.strip() for p in value.split(',') if p.strip()]


# SECURITY
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-ez6gwzo(_$b*sfsu^&v2la_2$-^c-bfbkz0ee%w^hf6klgf-@$')
DEBUG = _bool_env(os.getenv('DEBUG'), True)
ALLOWED_HOSTS = _list_env(os.getenv('ALLOWED_HOSTS'), ['127.0.0.1', 'localhost'])


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third-party
    'rest_framework',

    # Local apps
    'apps.users',
    'apps.restaurants',
    'apps.tables',
    'apps.sessions',
    'apps.menu',
    'apps.orders',
    'apps.payments',
    'apps.inventory',
    'apps.staff',
    'apps.reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Use the config package urls as canonical
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI application now provided by config.wsgi
WSGI_APPLICATION = 'config.wsgi.application'


# Database
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    try:
        import dj_database_url  # optional

        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600),
        }
    except Exception:
        DATABASE_URL = None

if not DATABASE_URL:
    DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.sqlite3')
    if DB_ENGINE == 'django.db.backends.sqlite3':
        DATABASES = {
            'default': {
                'ENGINE': DB_ENGINE,
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': DB_ENGINE,
                'NAME': os.getenv('DB_NAME', 'menu_order_local'),
                'USER': os.getenv('DB_USER', 'root'),
                'PASSWORD': os.getenv('DB_PASSWORD', ''),
                'HOST': os.getenv('DB_HOST', '127.0.0.1'),
                'PORT': os.getenv('DB_PORT', '3306'),
                'OPTIONS': {},
            }
        }

# PyMySQL shim registration (safe if PyMySQL is installed)
try:
    if 'mysql' in (os.getenv('DB_ENGINE', '') or os.getenv('DATABASE_URL', '')):
        import pymysql  # type: ignore

        pymysql.install_as_MySQLdb()
except Exception:
    pass


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
