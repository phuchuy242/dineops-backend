from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


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

        # rate-limit / lockout settings
        max_attempts = getattr(settings, 'LOGIN_MAX_ATTEMPTS', 5)
        lockout_seconds = getattr(settings, 'LOGIN_LOCKOUT_SECONDS', 300)

        cache_key = f"login_attempts:{user_name}"

        # Try to find user instance if exists (to check locked_until)
        user_obj = None
        if '@' in user_name:
            user_obj = User.objects.filter(email=user_name).first()
        else:
            user_obj = User.objects.filter(user_name=user_name).first()

        if user_obj and user_obj.locked_until and user_obj.locked_until > timezone.now():
            raise serializers.ValidationError({"detail": "Account locked due to too many failed login attempts"})

        user = None

        # Nếu là email
        if '@' in user_name:
            user = authenticate(username=user_name, password=password)
        else:
            # Nếu là username
            try:
                user_lookup = User.objects.get(user_name=user_name)
                user = authenticate(username=user_lookup.email, password=password)
            except User.DoesNotExist:
                user = None

        if not user:
            # increment attempt
            attempts = cache.get(cache_key, 0) + 1
            cache.set(cache_key, attempts, timeout=lockout_seconds)

            # If exceeded max attempts, lock account if user exists
            if attempts >= max_attempts and user_obj:
                user_obj.locked_until = timezone.now() + timedelta(seconds=lockout_seconds)
                user_obj.save(update_fields=['locked_until'])
                # reset attempts
                cache.delete(cache_key)
                raise serializers.ValidationError({"detail": "Account locked due to too many failed login attempts"})

            raise serializers.ValidationError(
                {"detail": "Username or password is incorrect"}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "User account is disabled"}
            )

        # Success -> clear attempts
        cache.delete(cache_key)

        attrs['user'] = user
        return attrs
