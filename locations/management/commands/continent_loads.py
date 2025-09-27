import json
from django.core.management.base import BaseCommand
from locations.models import Continent

# Hardcoded JSON data
CONTINENTS_DATA = [
    {
        "name": "Asia",
        "population": 4761000000,
        "area_sq_km": 44579000
    },
    {
        "name": "Africa",
        "population": 1460000000,
        "area_sq_km": 30370000
    },
    {
        "name": "Europe",
        "population": 750000000,
        "area_sq_km": 10180000
    },
    {
        "name": "North America",
        "population": 610000000,
        "area_sq_km": 24709000
    },
    {
        "name": "South America",
        "population": 440000000,
        "area_sq_km": 17840000
    },
    {
        "name": "Australia (Oceania)",
        "population": 46000000,
        "area_sq_km": 8600000
    },
    {
        "name": "Antarctica",
        "population": 1000,
        "area_sq_km": 14200000
    }
]


class Command(BaseCommand):
    help = "Load continents into the database"

    def handle(self, *args, **options):
        for data in CONTINENTS_DATA:
            obj, created = Continent.objects.update_or_create(
                name=data["name"],
                defaults={
                    "population": data["population"],
                    "area_sq_km": data["area_sq_km"]
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created continent: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated continent: {obj.name}"))

        self.stdout.write(self.style.SUCCESS("✅ Continents loaded successfully!"))
