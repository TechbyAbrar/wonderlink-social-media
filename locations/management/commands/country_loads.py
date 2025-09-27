from django.core.management.base import BaseCommand
from locations.models import Country, COUNTRY_CHOICES

class Command(BaseCommand):
    help = "Load or sync all countries from COUNTRY_CHOICES into the database without duplicates."

    def handle(self, *args, **kwargs):
        created_count = 0
        updated_count = 0

        for code, name in COUNTRY_CHOICES:
            obj, created = Country.objects.update_or_create(
                country_code=code,
                defaults={
                    "constituent_of": "",
                    "region": "",
                    "capital": "",
                    "status": "",
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {name} ({code})"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"Updated: {name} ({code})"))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! {created_count} created, {updated_count} updated."
        ))
