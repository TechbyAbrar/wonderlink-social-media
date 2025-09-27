from rest_framework import serializers
from .models import Leaderboard

class LeaderboardSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id",read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    profile_pic = serializers.ImageField(source="user.profile_pic", read_only=True)
    rank = serializers.IntegerField(read_only=True)

    class Meta:
        model = Leaderboard
        fields = [
            "id",
            "rank",
            "username",
            "full_name",
            "email",
            "profile_pic",
            "score",
            "total",
            "percentage",
        ]




from rest_framework import serializers

class DashboardSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    new_users_by_month = serializers.DictField(child=serializers.IntegerField())
    total_travelled_users = serializers.IntegerField()
    user_growth_by_month = serializers.DictField(child=serializers.IntegerField())
    most_visited_countries = serializers.ListField(child=serializers.DictField())
