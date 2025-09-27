# accounts/management/commands/sync_lives_in.py
from django.core.management.base import BaseCommand
from accounts.models import UserAuth
from locations.models import TravelRecord

class Command(BaseCommand):
    help = "Sync existing users' lives_in with TravelRecord"

    def handle(self, *args, **kwargs):
        users = UserAuth.objects.exclude(lives_in=None)
        count = 0
        for user in users:
            travel_record, created = TravelRecord.objects.get_or_create(
                user=user,
                country=user.lives_in,
                defaults={'visited': True, 'lived_here': True}
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
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Synced {count} users' lives_in data."))
