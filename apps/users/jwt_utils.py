import jwt
import hashlib
import uuid as _uuid
from datetime import datetime, timedelta, timezone
from django.conf import settings


def _get_secret_and_algo():
    secret_key = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
    algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')
    return secret_key, algorithm


def _env_sig(user):
    """Generate environment signature for user validation."""
    env_data = f"{user.uuid}{user.user_name}{user.is_active}"
    return hashlib.sha256(env_data.encode()).hexdigest()


def hash_token(token: str) -> str:
    """Hash a token string for safe storage/comparison."""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_access_token(user, extra_payload=None):
    """
    Generate access token (short lived).

    Args:
        user: User instance
        extra_payload: Additional claims to include in the payload

    Returns:
        str: JWT access token
    """
    secret_key, algorithm = _get_secret_and_algo()
    now = datetime.now(timezone.utc)
    access_minutes = getattr(settings, 'JWT_ACCESS_EXP_MINUTES', 15)
    exp = now + timedelta(minutes=access_minutes)

    payload = {
        'user_id': user.id,
        'uuid': str(user.uuid),
        'email': user.email,
        'user_name': user.user_name,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'iat': int(now.timestamp()),
        'exp': int(exp.timestamp()),
        'env_sig': _env_sig(user),
        'token_type': 'access',
    }

    if extra_payload:
        payload.update(extra_payload)

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


def generate_refresh_token(user):
    """
    Generate refresh token (long lived).

    Args:
        user: User instance

    Returns:
        tuple: (refresh_token_string, jti, expires_at)
    """
    secret_key, algorithm = _get_secret_and_algo()
    now = datetime.now(timezone.utc)
    refresh_days = getattr(settings, 'JWT_REFRESH_EXP_DAYS', 7)
    exp = now + timedelta(days=refresh_days)

    jti = _uuid.uuid4()

    payload = {
        'user_id': user.id,
        'uuid': str(user.uuid),
        'jti': str(jti),
        'iat': int(now.timestamp()),
        'exp': int(exp.timestamp()),
        'token_type': 'refresh',
    }

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    if isinstance(token, bytes):
        token = token.decode('utf-8')

    return token, jti, exp


def decode_jwt(token: str, verify=True) -> dict:
    """
    Decode JWT and return payload.

    Args:
        token: JWT token string
        verify: Whether to verify signature and expiration

    Returns:
        dict: Decoded payload

    Raises:
        jwt.ExpiredSignatureError: Token has expired
        jwt.InvalidTokenError: Token is invalid
    """
    secret_key, algorithm = _get_secret_and_algo()

    options = {}
    if not verify:
        options = {
            'verify_signature': False,
            'verify_exp': False,
        }

    payload = jwt.decode(token, secret_key, algorithms=[algorithm], options=options)
    return payload


def verify_token(token: str, expected_type: str = 'access') -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string
        expected_type: Expected token type ('access' or 'refresh')

    Returns:
        dict: Decoded payload if valid

    Raises:
        jwt.ExpiredSignatureError: Token has expired
        jwt.InvalidTokenError: Token is invalid or wrong type
    """
    payload = decode_jwt(token)

    token_type = payload.get('token_type')
    if token_type != expected_type:
        raise jwt.InvalidTokenError(f'Expected {expected_type} token, got {token_type}')

    return payload
