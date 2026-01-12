import jwt
import hashlib
from datetime import datetime, timedelta, timezone
from django.conf import settings


def _get_secret_and_algo():
    secret_key = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
    algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')
    return secret_key, algorithm


def _env_sig(user):
    env_data = f"{user.uuid}{user.user_name}{user.is_active}"
    return hashlib.sha256(env_data.encode()).hexdigest()


def hash_token(token: str) -> str:
    """Hash a token string for safe storage/comparison."""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_access_token(user):
    """Generate access token (short lived)."""
    secret_key, algorithm = _get_secret_and_algo()
    now = datetime.now(timezone.utc)
    access_minutes = getattr(settings, 'JWT_ACCESS_EXP_MINUTES', 15)
    exp = now + timedelta(minutes=access_minutes)

    payload = {
        'uuid': str(user.uuid),
        'user_name': user.user_name,
        'active': user.is_active,
        'iat': int(now.timestamp()),
        'exp': int(exp.timestamp()),
        'env_sig': _env_sig(user),
        'roles': [],
        'token_type': 'access',
    }

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    if isinstance(token, bytes):
        token = token.decode()
    return token




def decode_jwt(token: str) -> dict:
    """Decode JWT and return payload, raising jwt exceptions on failure."""
    secret_key, algorithm = _get_secret_and_algo()
    # This will raise jwt.ExpiredSignatureError or jwt.InvalidTokenError which caller should handle
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    return payload
