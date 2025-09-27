from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserAuth
from locations.models import TravelRecord

@receiver(post_save, sender=UserAuth)
def sync_lives_in_travel_record(sender, instance, **kwargs):
    """
    Ensures that the country in 'lives_in' is recorded in TravelRecord
    as visited and lived_here.
    """
    if instance.lives_in:
        travel_record, _ = TravelRecord.objects.get_or_create(
            user=instance,
            country=instance.lives_in,
            defaults={
                'visited': True,
                'lived_here': True
            }
        )
        updated = False
        if not travel_record.visited:
            travel_record.visited = True
            updated = True
        if not travel_record.lived_here:
            travel_record.lived_here = True
            updated = True
        if updated:
            travel_record.save(update_fields=['visited', 'lived_here'])
