# leaderboard/admin.py
from django.contrib import admin
from .models import Leaderboard

@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ("user", "get_full_name", "score", "total", "percentage", "created_at")
    search_fields = ("user__username", "user__email", "user__full_name")
    readonly_fields = ("score", "total", "percentage", "created_at", "updated_at")

    def get_full_name(self, obj):
        return obj.user.full_name
    get_full_name.short_description = "Full Name"
