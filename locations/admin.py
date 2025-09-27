from django.contrib import admin
from .models import Country, Continent, TravelRecord

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        "country_name",  # property
        "country_code",  # PK
        "continent",
        "capital",
        "region",
        "population",
        "status",
    )
    list_filter = ("continent", "region", "status")
    search_fields = ("country_code", "continent__name", "capital", "region")
    ordering = ("country_code",)
    filter_horizontal = ("neighbouring_countries",)
    readonly_fields = ("country_name",)



@admin.register(Continent)
class ContinentAdmin(admin.ModelAdmin):
    list_display = ("name", "population", "area_sq_km")
    search_fields = ("name",)



@admin.register(TravelRecord)
class TravelRecordAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "country",
        "visited",
        "times_visited",
        "lived_here",
        "bucket_list",
        "favourite",
        "created_at",
        "updated_at",
    )
    list_filter = ("visited", "lived_here", "bucket_list", "favourite", "country")
    search_fields = ("user__username", "user__email", "country__country_name")
    readonly_fields = ("created_at", "updated_at")