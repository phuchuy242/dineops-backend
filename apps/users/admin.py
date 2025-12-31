from Tools.scripts.pindent import delete_filter
from django.contrib import admin
from .models import User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "email",
        "user_name",
        "is_active",
        "is_verified",
        "is_staff",
        "created_at",
    )
    search_fields = ("email", "user_name")
    list_filter = ("is_active", "is_verified", "is_staff")
    ordering = ("-created_at",)
