from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer, LoginSerializer
from .jwt_utils import generate_access_token, generate_refresh_token, decode_jwt, hash_token, _env_sig
from .models import RefreshToken

from django.utils import timezone
import jwt


def _format_response(status_val: int, code: int, msg: str, data: dict | None = None):
    """Standard response format used by users endpoints."""
    payload = {
        "status": int(bool(status_val)),
        "code": int(code),
        "msg": msg,
    }
    if data is not None:
        payload["data"] = data
    return payload


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            _format_response(False, status.HTTP_400_BAD_REQUEST, "Validation error", {"errors": serializer.errors}),
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = serializer.save()

    return Response(
        _format_response(True, status.HTTP_201_CREATED, "Register success", {
            "uuid": str(user.uuid),
            "user_name": user.user_name,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
        }),
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data, context={"request": request})

    if not serializer.is_valid():
        # prefer returning explicit serializer error detail if present (e.g. lockout)
        errors = serializer.errors
        # serializer.errors may be dict; try detail key or first error message
        msg = None
        if isinstance(errors, dict):
            msg = errors.get('detail') or errors.get('non_field_errors')
            if isinstance(msg, list):
                msg = msg[0] if msg else None
        if not msg:
            msg = "Username or password is incorrect"
        return Response(
            _format_response(0, 400, str(msg), {"errors": errors}),
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Get authenticated user
    user = serializer.validated_data["user"]

    # Generate tokens
    access_token = generate_access_token(user)
    refresh_token, jti, expires_at = generate_refresh_token(user)

    # Store hashed refresh token for stateful revoke/rotation
    token_hash = hash_token(refresh_token)
    RefreshToken.objects.create(user=user, jti=jti, token_hash=token_hash, expires_at=expires_at)

    # Update last login time
    user.last_login_at = timezone.now()
    user.save(update_fields=["last_login_at"])

    return Response(
        _format_response(1, 200, "login.successful", {"access": access_token, "refresh": refresh_token}),
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token(request):
    """Exchange a valid refresh token for a new access token (and rotate refresh token).

    Expected POST body: {"refresh": "<token>"}
    """
    refresh = request.data.get("refresh")
    if not refresh:
        return Response(_format_response(0, 400, "Missing refresh token"), status=status.HTTP_400_BAD_REQUEST)

    try:
        payload = decode_jwt(refresh)
    except jwt.ExpiredSignatureError:
        return Response(_format_response(0, 401, "Refresh token expired"), status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response(_format_response(0, 400, "Invalid refresh token"), status=status.HTTP_400_BAD_REQUEST)

    if payload.get("token_type") != "refresh":
        return Response(_format_response(0, 400, "Invalid token type"), status=status.HTTP_400_BAD_REQUEST)

    jti = payload.get("jti")
    uuid = payload.get("uuid")
    if not jti or not uuid:
        return Response(_format_response(0, 400, "Invalid token payload"), status=status.HTTP_400_BAD_REQUEST)

    # Find stored refresh token record
    try:
        token_obj = RefreshToken.objects.get(jti=jti, user__uuid=uuid)
    except RefreshToken.DoesNotExist:
        return Response(_format_response(0, 401, "Refresh token not found or revoked"), status=status.HTTP_401_UNAUTHORIZED)

    # Verify not revoked and not expired
    if token_obj.revoked:
        return Response(_format_response(0, 401, "Refresh token revoked"), status=status.HTTP_401_UNAUTHORIZED)

    now = timezone.now()
    if token_obj.expires_at and token_obj.expires_at < now:
        # revoke expired token
        token_obj.revoked = True
        token_obj.save(update_fields=["revoked"])
        return Response(_format_response(0, 401, "Refresh token expired"), status=status.HTTP_401_UNAUTHORIZED)

    # Verify env_sig matches current user state
    user = token_obj.user
    if payload.get('env_sig') != _env_sig(user):
        return Response(_format_response(0, 401, "Token environment mismatch"), status=status.HTTP_401_UNAUTHORIZED)

    # Validate token string matches stored hash (prevent database only token use)
    if token_obj.token_hash != hash_token(refresh):
        return Response(_format_response(0, 401, "Invalid refresh token"), status=status.HTTP_401_UNAUTHORIZED)

    # Rotate: revoke old token and issue new refresh + access
    token_obj.revoked = True
    token_obj.save(update_fields=["revoked"])

    user = token_obj.user
    access_token = generate_access_token(user)
    new_refresh, new_jti, new_exp = generate_refresh_token(user)
    new_hash = hash_token(new_refresh)
    RefreshToken.objects.create(user=user, jti=new_jti, token_hash=new_hash, expires_at=new_exp)

    # mark used
    token_obj.mark_used()

    return Response(_format_response(1, 200, "token.refreshed", {"access": access_token, "refresh": new_refresh}), status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def logout(request):
    """Revoke a refresh token (log out). Expect {"refresh": "..."} in POST body."""
    refresh = request.data.get("refresh")
    if not refresh:
        return Response(_format_response(0, 400, "Missing refresh token"), status=status.HTTP_400_BAD_REQUEST)

    try:
        payload = decode_jwt(refresh)
    except jwt.InvalidTokenError:
        return Response(_format_response(0, 400, "Invalid refresh token"), status=status.HTTP_400_BAD_REQUEST)

    if payload.get("token_type") != "refresh":
        return Response(_format_response(0, 400, "Invalid token type"), status=status.HTTP_400_BAD_REQUEST)

    jti = payload.get("jti")
    uuid = payload.get("uuid")
    if not jti or not uuid:
        return Response(_format_response(0, 400, "Invalid token payload"), status=status.HTTP_400_BAD_REQUEST)

    try:
        token_obj = RefreshToken.objects.get(jti=jti, user__uuid=uuid)
    except RefreshToken.DoesNotExist:
        return Response(_format_response(0, 404, "Refresh token not found"), status=status.HTTP_404_NOT_FOUND)

    # Verify env_sig matches current user state
    if payload.get('env_sig') != _env_sig(token_obj.user):
        return Response(_format_response(0, 401, "Token environment mismatch"), status=status.HTTP_401_UNAUTHORIZED)

    token_obj.revoke()

    return Response(_format_response(1, 200, "logged_out"), status=status.HTTP_200_OK)
