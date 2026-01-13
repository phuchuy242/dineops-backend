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
    'corsheaders',

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
    'apps.category',
    'apps.products',
    'apps.ingredient',
    'apps.dishingredient',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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

# If the chosen database backend is MySQL, ensure utf8mb4 and sane defaults
def _ensure_mysql_options(db_conf: dict):
    options = db_conf.setdefault('OPTIONS', {}) or {}
    # ensure proper charset for full unicode support (emoji)
    options.setdefault('charset', 'utf8mb4')
    # Set strict modes for safer SQL behavior
    options.setdefault('init_command', "SET sql_mode='STRICT_TRANS_TABLES', innodb_strict_mode=1")
    db_conf['OPTIONS'] = options
    # connection pooling / reuse
    try:
        db_conf['CONN_MAX_AGE'] = int(os.getenv('CONN_MAX_AGE', '600'))
    except Exception:
        db_conf['CONN_MAX_AGE'] = 600


# Apply MySQL-specific options if applicable (covers both dj_database_url and manual config)
if 'default' in locals() and isinstance(DATABASES, dict):
    engine = DATABASES.get('default', {}).get('ENGINE', '') or ''
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
AUTH_USER_MODEL = "users.User"

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = _bool_env(os.getenv('CORS_ALLOW_ALL_ORIGINS'), DEBUG)
CORS_ALLOWED_ORIGINS = _list_env(
    os.getenv('CORS_ALLOWED_ORIGINS'),
    ['http://localhost:3000', 'http://127.0.0.1:3000']
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = _list_env(
    os.getenv('CSRF_TRUSTED_ORIGINS'),
    ['http://localhost:3000', 'http://127.0.0.1:3000']
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'core.responses.StandardResultsSetPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

# JWT Settings
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 8

# Simple JWT Configuration - Only Access Token (No Refresh Token)
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_HOURS', '8'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=0),  # Disabled
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': JWT_ALGORITHM,
    'SIGNING_KEY': JWT_SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',
}

