import jwt
import hashlib
from datetime import datetime, timedelta, timezone
from django.conf import settings


def generate_jwt_token(user):
    """
    Generate JWT token for authenticated user
    """
    # Get secret key from settings or use a default (should be in settings)
    secret_key = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)

    # Create environment signature (simplified version)
    env_data = f"{user.uuid}{user.user_name}{user.is_active}"
    env_sig = hashlib.sha256(env_data.encode()).hexdigest()

    # Set token expiration (8 hours from now)
    iat = datetime.now(timezone.utc)
    exp = iat + timedelta(hours=8)

    # Create payload
    payload = {
        'uuid': str(user.uuid),
        'user_name': user.user_name,
        'active': user.is_active,
        'iat': int(iat.timestamp()),
        'exp': int(exp.timestamp()),
        'env_sig': env_sig,
        'roles': []  # Add roles here if you have role system
    }

    # Generate token
    token = jwt.encode(payload, secret_key, algorithm='HS256')

    return token
