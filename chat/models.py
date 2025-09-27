from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatThread(models.Model):
    user_a = models.ForeignKey(User, related_name="threads_as_a", on_delete=models.CASCADE)
    user_b = models.ForeignKey(User, related_name="threads_as_b", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user_a", "user_b")]
        indexes = [models.Index(fields=["user_a", "user_b"]), models.Index(fields=["updated_at"])]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Thread {self.pk} ({self.user_a_id} <-> {self.user_b_id})"

    @classmethod
    def get_or_create_thread(cls, user1, user2):
        from django.db import transaction
        a, b = (user1, user2) if user1.id < user2.id else (user2, user1)
        with transaction.atomic():
            thread, _ = cls.objects.get_or_create(user_a=a, user_b=b)
        return thread

class Message(models.Model):
    MESSAGE_TEXT = "text"
    MESSAGE_IMAGE = "image"
    MESSAGE_TYPES = [(MESSAGE_TEXT, "Text"), (MESSAGE_IMAGE, "Image")]

    thread = models.ForeignKey(ChatThread, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default=MESSAGE_TEXT)
    attachment = models.ImageField(upload_to="chat_attachments", null=True, blank=True)
    is_read = models.BooleanField(default=False)
    is_like = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["thread", "created_at"]), models.Index(fields=["sender", "created_at"])]

    def __str__(self):
        return f"Message {self.pk} in Thread {self.thread_id}"

class MessageReaction(models.Model):
    message = models.ForeignKey(Message, related_name="reactions", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=20)  # like, heart, emoji name
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("message", "user")
