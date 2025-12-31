from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer


@api_view(["POST"])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                "status": False,
                "code": status.HTTP_400_BAD_REQUEST,
                "msg": "Validation error",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = serializer.save()

    return Response(
        {
            "status": True,
            "code": status.HTTP_201_CREATED,
            "msg": "Register success",
            "data": {
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
            },
        },
        status=status.HTTP_201_CREATED,
    )
