from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "user_name",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "password_confirm",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "Password confirmation does not match"}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user

class LoginSerializer(serializers.Serializer):
    user_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user_name = attrs.get('user_name')
        password = attrs.get('password')

        user = None

        # Nếu là email
        if '@' in user_name:
            user = authenticate(username=user_name, password=password)
        else:
            # Nếu là username
            try:
                user_obj = User.objects.get(user_name=user_name)
                user = authenticate(username=user_obj.email, password=password)
            except User.DoesNotExist:
                pass

        if not user:
            raise serializers.ValidationError(
                {"detail": "Username or password is incorrect"}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "User account is disabled"}
            )

        attrs['user'] = user
        return attrs
