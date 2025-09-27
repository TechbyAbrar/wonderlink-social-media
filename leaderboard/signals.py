# leaderboard/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from locations.models import TravelRecord
from .utils import update_leaderboard

@receiver(post_save, sender=TravelRecord)
def update_leaderboard_on_travelrecord(sender, instance, **kwargs):
    """
    Automatically update leaderboard when a user updates a TravelRecord.
    """
    update_leaderboard(instance.user)
