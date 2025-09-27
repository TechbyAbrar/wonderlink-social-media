from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Follow, Report, Block



class FollowSerializer(serializers.ModelSerializer):
    follower_id = serializers.IntegerField(source='follower.id', read_only=True)
    followed_id = serializers.IntegerField(source='followed.id', read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower_id', 'followed_id', 'status', 'created_at']


class FollowerRequestSerializer(serializers.ModelSerializer):
    follower_id = serializers.IntegerField(source='follower.id', read_only=True)
    follower_email = serializers.EmailField(source='follower.email', read_only=True)
    follower_name = serializers.CharField(source='follower.get_full_name', read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower_id', 'follower_name', 'follower_email', 'status', 'created_at']
        
        
from rest_framework import serializers
from accounts.models import UserAuth
from .models import Follow


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAuth
        fields = ["id", "email", "full_name", "profile_pic"]


class FollowSerializer(serializers.ModelSerializer):
    requester = UserMiniSerializer(read_only=True)
    receiver = UserMiniSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "requester", "receiver", "status", "created_at"]


        


class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Report
        fields = ["id", "reporter", "reported_user", "reason", "details", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        if data["reporter"] == data["reported_user"]:
            raise serializers.ValidationError("You cannot report yourself.")
        return data


from rest_framework import serializers
from .models import Block

class BlockSerializer(serializers.ModelSerializer):
    blocker = serializers.HiddenField(default=serializers.CurrentUserDefault())
    full_name = serializers.CharField(source="blocked_user.full_name", read_only=True)
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = Block
        fields = [
            "id",
            "blocker",
            "blocked_user",
            "full_name",
            "profile_pic",
            "created_at"
        ]
        read_only_fields = ["id", "blocker", "created_at"]

    def get_profile_pic(self, obj):
        request = self.context.get("request")
        if obj.blocked_user.profile_pic and request:
            return request.build_absolute_uri(obj.blocked_user.profile_pic.url)
        return None




class FollowActionSerializer(serializers.ModelSerializer):
    follower_id = serializers.IntegerField(source='follower.id', read_only=True)
    follower_email = serializers.EmailField(source='follower.email', read_only=True)
    follower_name = serializers.CharField(source='follower.get_full_name', read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower_id', 'follower_name', 'follower_email', 'status', 'created_at']







# mutual

from rest_framework import serializers
from accounts.models import UserAuth
from locations.models import TravelRecord

class FriendTravelSerializer(serializers.ModelSerializer):
    visited = serializers.SerializerMethodField()
    lived_in = serializers.SerializerMethodField()
    bucket_list = serializers.SerializerMethodField()
    favourite = serializers.SerializerMethodField()

    class Meta:
        model = UserAuth
        fields = [
            "id",
            "full_name",
            "username",
            "email",
            "profile_pic",
            "visited",
            "lived_in",
            "bucket_list",
            "favourite"
        ]

    def get_visited(self, obj):
        return list(TravelRecord.objects.filter(user=obj, visited=True)
                    .values_list("country__country_code", flat=True))

    def get_lived_in(self, obj):
        return list(TravelRecord.objects.filter(user=obj, lived_here=True)
                    .values_list("country__country_code", flat=True))

    def get_bucket_list(self, obj):
        return list(TravelRecord.objects.filter(user=obj, bucket_list=True)
                    .values_list("country__country_code", flat=True))

    def get_favourite(self, obj):
        return list(TravelRecord.objects.filter(user=obj, favourite=True)
                    .values_list("country__country_code", flat=True))
