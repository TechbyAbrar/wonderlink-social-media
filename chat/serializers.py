from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatThread, Message, MessageReaction

User = get_user_model()

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "full_name", "profile_pic"]

# class MessageSerializer(serializers.ModelSerializer):
#     sender = SimpleUserSerializer(read_only=True)
#     reactions = serializers.SerializerMethodField()

#     class Meta:
#         model = Message
#         fields = [
#             "id", "thread", "sender", "content", "message_type", "attachment",
#             "is_read", "is_like", "created_at", "reactions"
#         ]
#         read_only_fields = ["id", "sender", "created_at", "is_read", "reactions"]

#     def get_reactions(self, obj):
#         # Use pre-fetched reactions to avoid lazy DB queries in async context
#         reactions = getattr(obj, "_prefetched_reactions", obj.reactions.all())
#         return [{"user_id": r.user_id, "reaction": r.reaction} for r in reactions]

#     def validate(self, attrs):
#         mt = attrs.get("message_type", Message.MESSAGE_TEXT)
#         if mt == Message.MESSAGE_TEXT and not attrs.get("content"):
#             raise serializers.ValidationError({"content": "Text message requires 'content'."})
#         if mt == Message.MESSAGE_IMAGE and not attrs.get("attachment"):
#             raise serializers.ValidationError({"attachment": "Image message requires an 'attachment'."})
#         return attrs

#     def create(self, validated_data):
#         user = self.context["request"].user
#         validated_data["sender"] = user
#         message = super().create(validated_data)
#         # update thread timestamp
#         ChatThread.objects.filter(pk=message.thread_id).update(updated_at=message.created_at)
#         return message

# class ThreadListSerializer(serializers.ModelSerializer):
#     other_user = serializers.SerializerMethodField()
#     last_message = serializers.SerializerMethodField()

#     class Meta:
#         model = ChatThread
#         fields = ["id", "other_user", "updated_at", "last_message"]

#     def get_other_user(self, obj):
#         request_user = self.context.get("request").user
#         other = obj.user_b if obj.user_a_id == request_user.id else obj.user_a
#         return SimpleUserSerializer(other).data

#     def get_last_message(self, obj):
#         last = obj.messages.order_by("-created_at").first()
#         return MessageSerializer(last).data if last else None

class MessageSerializer(serializers.ModelSerializer):
    message_id = serializers.IntegerField(source="id", read_only=True)
    sender = SimpleUserSerializer(read_only=True)
    reactions = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "message_id", "thread", "sender", "content", "message_type", "attachment",
            "is_read", "is_like", "created_at", "reactions"
        ]
        read_only_fields = ["message_id", "sender", "created_at", "is_read", "reactions"]

    def get_reactions(self, obj):
        # Use pre-fetched reactions to avoid lazy DB queries in async context
        reactions = getattr(obj, "_prefetched_reactions", obj.reactions.all())
        return [{"user_id": r.user_id, "reaction": r.reaction} for r in reactions]

    def validate(self, attrs):
        mt = attrs.get("message_type", Message.MESSAGE_TEXT)
        if mt == Message.MESSAGE_TEXT and not attrs.get("content"):
            raise serializers.ValidationError({"content": "Text message requires 'content'."})
        if mt == Message.MESSAGE_IMAGE and not attrs.get("attachment"):
            raise serializers.ValidationError({"attachment": "Image message requires an 'attachment'."})
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["sender"] = user
        message = super().create(validated_data)
        # update thread timestamp
        ChatThread.objects.filter(pk=message.thread_id).update(updated_at=message.created_at)
        return message



class ThreadListSerializer(serializers.ModelSerializer):
    thread_id = serializers.IntegerField(source="id", read_only=True)
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatThread
        fields = ["thread_id", "other_user", "updated_at", "last_message"]

    def get_other_user(self, obj):
        request_user = self.context.get("request").user
        other = obj.user_b if obj.user_a_id == request_user.id else obj.user_a
        return SimpleUserSerializer(other).data

    def get_last_message(self, obj):
        last = obj.messages.order_by("-created_at").first()
        return MessageSerializer(last).data if last else None
