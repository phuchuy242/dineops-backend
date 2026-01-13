from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken as SimpleJWTRefreshToken
from core.responses import success_response, error_response
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    PasswordChangeSerializer,
    RefreshTokenSerializer,
)
from .models import RefreshToken
import jwt
import hashlib


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):

    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return error_response(
            msg="Dữ liệu không hợp lệ",
            errors=serializer.errors,
            code=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Create user
        user = serializer.save()

        # Generate tokens using SimpleJWT
        refresh = SimpleJWTRefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token_str = str(refresh)

        # Store refresh token in database
        RefreshToken.objects.create(
            jti=str(refresh['jti']),
            user=user,
            token_hash=hashlib.sha256(refresh_token_str.encode()).hexdigest(),
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )

        # Serialize user data
        user_data = UserSerializer(user).data

        data = {
            'access_token': access_token,
            'refresh_token': refresh_token_str,
            'token_type': 'Bearer',
            'expires_in': 900,  # 15 minutes in seconds
            'user': user_data
        }

        return success_response(
            data=data,
            msg='User registered successfully',
            code=status.HTTP_201_CREATED
        )

    except Exception as e:
        return error_response(
            msg=f'Registration failed: {str(e)}',
            code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    User login.

    Request body:
    {
        "identifier": "user@example.com",  # Email, Username, or Phone Number
        "password": "SecurePass123"
    }

    Or specific fields:
    {
        "email": "user@example.com",
        "password": "SecurePass123"
    }

    Response:
    {
        "status": true,
        "code": 200,
        "msg": "Đăng nhập thành công",
        "data": {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_type": "Bearer",
            "expires_in": 900,
            "user": {
                "id": 1,
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                ...
            }
        }
    }
    """
    serializer = LoginSerializer(data=request.data, context={'request': request})

    if not serializer.is_valid():
        return error_response(
            msg="Login failed",
            errors=serializer.errors,
            code=status.HTTP_401_UNAUTHORIZED
        )

    try:
        user = serializer.validated_data['user']

        # Generate tokens using SimpleJWT
        refresh = SimpleJWTRefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token_str = str(refresh)

        # Store refresh token in database
        RefreshToken.objects.create(
            jti=str(refresh['jti']),
            user=user,
            token_hash=hashlib.sha256(refresh_token_str.encode()).hexdigest(),
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )

        # Serialize user data
        user_data = UserSerializer(user).data

        data = {
            'access_token': access_token,
            'refresh_token': refresh_token_str,
            'token_type': 'Bearer',
            'expires_in': 900,  # 15 minutes in seconds
            'user': user_data
        }

        return success_response(
            data=data,
            msg='Login successful',
            code=status.HTTP_200_OK
        )

    except Exception as e:
        return error_response(
            msg=f'Login failed: {str(e)}',
            code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh access token using refresh token.

    Request body:
    {
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }

    Response:
    {
        "status": true,
        "code": 200,
        "msg": "Token đã được làm mới",
        "data": {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_type": "Bearer",
            "expires_in": 900
        }
    }
    """
    serializer = RefreshTokenSerializer(data=request.data)

    if not serializer.is_valid():
        return error_response(
            msg="Invalid data",
            errors=serializer.errors,
            code=status.HTTP_400_BAD_REQUEST
        )

    refresh_token_str = serializer.validated_data['refresh_token']

    try:
        # Verify and decode refresh token using SimpleJWT
        refresh = SimpleJWTRefreshToken(refresh_token_str)
        user_id = refresh.get('user_id')
        jti = str(refresh.get('jti'))

        # Check if refresh token exists and is valid in database
        token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()
        refresh_token_obj = RefreshToken.objects.filter(
            jti=jti,
            token_hash=token_hash,
            user_id=user_id,
            revoked=False,
            expires_at__gt=timezone.now()
        ).first()

        if not refresh_token_obj:
            return error_response(
                msg="Refresh token is invalid or has expired",
                code=status.HTTP_401_UNAUTHORIZED
            )

        # Get user
        user = refresh_token_obj.user

        if not user.is_active:
            return error_response(
                msg="Account has been disabled",
                code=status.HTTP_401_UNAUTHORIZED
            )

        # Mark refresh token as used
        refresh_token_obj.mark_used()

        # Generate new access token using SimpleJWT
        access_token = str(refresh.access_token)

        data = {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 900,
        }

        return success_response(
            data=data,
            msg='Token refreshed successfully',
            code=status.HTTP_200_OK
        )

    except jwt.ExpiredSignatureError:
        return error_response(
            msg="Refresh token has expired",
            code=status.HTTP_401_UNAUTHORIZED
        )
    except jwt.InvalidTokenError as e:
        return error_response(
            msg=f"Invalid refresh token: {str(e)}",
            code=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        return error_response(
            msg=f"Token refresh failed: {str(e)}",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    User logout - revokes all refresh tokens.

    Request body (optional):
    {
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."  # If provided, revokes only this token
    }

    Response:
    {
        "status": true,
        "code": 200,
        "msg": "Đăng xuất thành công"
    }
    """
    user = request.user
    refresh_token_str = request.data.get('refresh_token')

    try:
        if refresh_token_str:
            # Revoke specific refresh token
            token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()
            RefreshToken.objects.filter(
                user=user,
                token_hash=token_hash,
                revoked=False
            ).update(revoked=True)
        else:
            # Revoke all refresh tokens for this user
            RefreshToken.objects.filter(
                user=user,
                revoked=False
            ).update(revoked=True)

        return success_response(
            msg='Logged out successfully',
            code=status.HTTP_200_OK
        )

    except Exception as e:
        return error_response(
            msg=f'Logout failed: {str(e)}',
            code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Get current user profile.

    Response:
    {
        "status": true,
        "code": 200,
        "msg": "User profile retrieved successfully",
        "data": {
            "id": 1,
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "user_name": "username",
            "full_name": "John Doe",
            ...
        }
    }
    """
    user = request.user
    user_data = UserSerializer(user).data

    return success_response(
        data=user_data,
        msg='User profile retrieved successfully',
        code=status.HTTP_200_OK
    )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update current user profile.

    Request body:
    {
        "first_name": "John",
        "last_name": "Doe",
        "avatar_url": "https://example.com/avatar.jpg"
    }

    Response:
    {
        "status": true,
        "code": 200,
        "msg": "Cập nhật thông tin thành công",
        "data": {
            "id": 1,
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            ...
        }
    }
    """
    user = request.user

    # Only allow updating certain fields
    allowed_fields = ['first_name', 'last_name', 'avatar_url']

    try:
        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])

        user.save()
        user_data = UserSerializer(user).data

        return success_response(
            data=user_data,
            msg='Profile updated successfully',
            code=status.HTTP_200_OK
        )

    except Exception as e:
        return error_response(
            msg=f'Update failed: {str(e)}',
            code=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password.

    Request body:
    {
        "old_password": "OldPass123",
        "new_password": "NewPass123",
        "new_password_confirm": "NewPass123"
    }

    Response:
    {
        "status": true,
        "code": 200,
        "msg": "Password changed successfully"
    }
    """
    serializer = PasswordChangeSerializer(
        data=request.data,
        context={'request': request}
    )

    if not serializer.is_valid():
        return error_response(
            msg="Invalid data",
            errors=serializer.errors,
            code=status.HTTP_400_BAD_REQUEST
        )

    try:
        serializer.save()

        # Revoke all refresh tokens after password change for security
        RefreshToken.objects.filter(
            user=request.user,
            revoked=False
        ).update(revoked=True)

        return success_response(
            msg='Password changed successfully. Please login again.',
            code=status.HTTP_200_OK
        )

    except Exception as e:
        return error_response(
            msg=f'Password change failed: {str(e)}',
            code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
