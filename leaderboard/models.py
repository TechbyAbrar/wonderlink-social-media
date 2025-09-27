# leaderboard/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Leaderboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="leaderboard")
    score = models.PositiveIntegerField(default=0)   # visited countries
    total = models.PositiveIntegerField(default=0)   # total countries in DB
    percentage = models.FloatField(default=0.0)      # score / total * 100
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_percentage(self):
        self.percentage = (self.score / self.total * 100) if self.total > 0 else 0
        self.save(update_fields=["score", "total", "percentage"])
