# friend_system/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db import transaction


from django.db import models, transaction
from django.conf import settings


class Follow(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    )

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="following", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="followers", on_delete=models.CASCADE
    )

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["requester", "receiver"]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.requester_id == self.receiver_id:
            raise ValueError("You cannot follow yourself.")
        super().save(*args, **kwargs)

    # --- Core actions ---
    @classmethod
    def send_request(cls, requester, receiver):
        if requester.id == receiver.id:
            raise ValueError("You cannot follow yourself.")

        with transaction.atomic():
            obj, created = cls.objects.get_or_create(
                requester=requester,
                receiver=receiver,
                defaults={"status": "pending"},
            )
            if not created and obj.status != "accepted":
                obj.status = "pending"
                obj.save(update_fields=["status"])
        return obj

    def accept(self):
        if self.status == "pending":
            self.status = "accepted"
            self.save(update_fields=["status"])

    def reject(self):
        if self.status == "pending":
            self.status = "rejected"
            self.save(update_fields=["status"])

    def followback(self):
        with transaction.atomic():
            if self.status == "pending":
                self.accept()

            reverse, created = Follow.objects.get_or_create(
                requester=self.receiver,
                receiver=self.requester,
                defaults={"status": "accepted"},
            )
            if not created and reverse.status != "accepted":
                reverse.status = "accepted"
                reverse.save(update_fields=["status"])




class Report(models.Model):
    REPORT_CHOICES = [
        ('spam', 'Spams or Scams'),
        ('harassment', 'Harassment or Bullying'),
        ('hate', 'Hate Speech or Violence'),
        ('nudity', 'Nudity or Sexual Content'),
        ('misinformation', 'Misinformation'),
        ('ip_violation', 'Intellectual Property Violation'),
        ('impersonation', 'Impersonation'),
        ('other', 'Other'),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reports_made",
        on_delete=models.CASCADE
    )
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reports_received",
        on_delete=models.CASCADE
    )
    reason = models.CharField(max_length=50, choices=REPORT_CHOICES)
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["reporter", "reported_user", "reason"]

    def __str__(self):
        return f"{self.reporter} → {self.reported_user} ({self.reason})"


class Block(models.Model):
    blocker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="blocks_made",
        on_delete=models.CASCADE
    )
    blocked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="blocks_received",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["blocker", "blocked_user"]

    def __str__(self):
        return f"{self.blocker} blocked {self.blocked_user}"
