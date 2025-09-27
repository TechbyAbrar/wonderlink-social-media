from django.contrib import admin
from .models import UserAuth

@admin.register(UserAuth)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        "email",
        "username",
        "full_name",
        "country",
        "lives_in",
        "is_verified",
        "is_staff",
        "is_superuser",
        "date_joined",
    )
    list_filter = ("is_verified", "is_staff", "is_superuser", "country", "lives_in")
    search_fields = ("email", "username", "full_name", "phone")
    ordering = ("-date_joined",)