from .base import *  # noqa: F401,F403

# Load dotenv again in case environment hasn't been loaded elsewhere (safe no-op)
from dotenv import load_dotenv
import os
load_dotenv()

# Local DB override: use SQLite by default for quick local development.
# Set FORCE_SQLITE=False in your .env to use DATABASE_URL/MySQL instead.
FORCE_SQLITE = os.getenv('FORCE_SQLITE', 'True').lower() in ('1', 'true', 'yes', 'on')
DATABASE_URL = os.getenv('DATABASE_URL')

if FORCE_SQLITE or not DATABASE_URL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Fallback to parsing DATABASE_URL (e.g. mysql://...)
    try:
        import dj_database_url

        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL, conn_max_age=int(os.getenv('CONN_MAX_AGE', '600'))),
        }
    except Exception:
        # keep DATABASES from base if parsing fails
        pass

# Keep local-specific overrides here
AUTH_USER_MODEL = globals().get('AUTH_USER_MODEL', 'core.User')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
