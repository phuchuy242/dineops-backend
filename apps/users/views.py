from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import authenticate
from core.responses import success_response, error_response
from .models import User


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user

    Request body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return error_response(
            msg='Email and password are required',
            code=status.HTTP_400_BAD_REQUEST
        )

    # Check if user already exists
    if User.objects.filter(email=email).exists():
        return error_response(
            msg='User with this email already exists',
            code=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Create user
        user = User.objects.create_user(email=email, password=password)

        # Generate access token
        access_token = AccessToken.for_user(user)

        data = {
            'access_token': str(access_token),
            'token_type': 'Bearer',
            'user': {
                'id': user.id,
                'email': user.email,
                'is_staff': user.is_staff,
            }
        }

        return success_response(
            data=data,
            msg='Registration successful',
            code=status.HTTP_201_CREATED
        )
    except Exception as e:
        return error_response(
            msg=f'Registration failed: {str(e)}',
            code=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login endpoint that returns only access token (no refresh token)

    Request body:
    {
        "email": "user@example.com",
        "password": "password123"
    }

    Response:
    {
        "status": true,
        "code": 200,
        "msg": "Login successful",
        "data": {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_type": "Bearer",
            "user": {
                "id": 1,
                "email": "user@example.com"
            }
        }
    }
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return error_response(
            msg='Email and password are required',
            code=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=email, password=password)

    if user is None:
        return error_response(
            msg='Invalid email or password',
            code=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return error_response(
            msg='Account is inactive',
            code=status.HTTP_403_FORBIDDEN
        )

    # Generate only access token
    access_token = AccessToken.for_user(user)

    data = {
        'access_token': str(access_token),
        'token_type': 'Bearer',
        'user': {
            'id': user.id,
            'email': user.email,
            'is_staff': user.is_staff,
        }
    }

    return success_response(
        data=data,
        msg='Login successful',
        code=status.HTTP_200_OK
    )


@api_view(['POST'])
def logout(request):
    """
    Logout endpoint

    Since we're using stateless JWT tokens without refresh tokens,
    logout is handled on the client side by removing the access token.
    """
    return success_response(
        msg='Logout successful',
        code=status.HTTP_200_OK
    )


@api_view(['GET'])
def profile(request):
    """
    Get current user profile

    Response:
    {
        "status": true,
        "code": 200,
        "msg": "Profile retrieved successfully",
        "data": {
            "id": 1,
            "email": "user@example.com",
            "is_staff": true,
            "is_active": true,
            "created_at": "2026-01-12 10:00:00"
        }
    }
    """
    user = request.user

    from core.fields import TimestampField

    data = {
        'id': user.id,
        'email': user.email,
        'is_staff': user.is_staff,
        'is_active': user.is_active,
        'created_at': TimestampField().to_representation(user.created_at),
    }

    return success_response(
        data=data,
        msg='Profile retrieved successfully',
        code=status.HTTP_200_OK
    )

