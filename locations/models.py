from django.db import models
from django.conf import settings
from .country_choices import COUNTRY_CHOICES


class Continent(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Full name of the continent, e.g. 'Europe', 'Asia'."
    )
    population = models.BigIntegerField(null=True, blank=True, help_text="Optional population of the continent")
    area_sq_km = models.BigIntegerField(null=True, blank=True, help_text="Total land area in square kilometers")

    class Meta:
        verbose_name_plural = "Continents"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Country(models.Model):
    country_logo = models.ImageField(upload_to="country_logos/", null=True, blank=True)
    country_code = models.CharField(
        max_length=7,
        primary_key=True,
        choices=COUNTRY_CHOICES
    )
    constituent_of = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    capital = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    continent = models.ForeignKey(
        Continent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="countries"
    )
    neighbouring_countries = models.ManyToManyField("self", blank=True, symmetrical=True)
    official_language = models.CharField(max_length=100, null=True, blank=True)
    population = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ["country_code"]

    def __str__(self):
        return f"{self.get_country_code_display()} ({self.country_code})"

    @property
    def country_name(self):
        return self.get_country_code_display()


class TravelRecord(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="travel_records"
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="travel_records"
    )
    
    visited = models.BooleanField(default=False)
    times_visited = models.PositiveIntegerField(default=0)
    
    lived_here = models.BooleanField(default=False)
    bucket_list = models.BooleanField(default=False)
    favourite = models.BooleanField(default=False)
    
    # add_photos = models.ImageField(upload_to="travel_photos/", null=True, blank=True)
    # photos_title = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "country")

    def __str__(self):
        return f"{self.user} - {self.country.country_name}"


class TravelPhoto(models.Model):
    travel_record = models.ForeignKey(
        TravelRecord,
        on_delete=models.CASCADE,
        related_name="photos"
    )
    image = models.ImageField(upload_to="travel_photos/")
    title = models.CharField(max_length=255, blank=True, null=True)  # optional
    month = models.PositiveSmallIntegerField(blank=True, null=True)   # optional
    year = models.PositiveSmallIntegerField(blank=True, null=True)    # optional

    class Meta:
        ordering = ['year', 'month']

    def __str__(self):
        return f"{self.travel_record.user} - {self.title or 'No Title'} ({self.month or '-'}/{self.year or '-'})"
