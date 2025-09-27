from django.core.management.base import BaseCommand
from accounts.models import UserAuth
from locations.models import TravelRecord

class Command(BaseCommand):
    help = "Sync all existing users' country and lives_in into TravelRecord"

    def handle(self, *args, **kwargs):
        users = UserAuth.objects.all()
        count = 0

        for user in users:
            try:
                user.sync_travel_records()
                count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to sync user {user.id}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully synced {count} users."))
