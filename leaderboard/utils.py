# leaderboard/utils.py
from .models import Leaderboard
from locations.models import TravelRecord, Country

def update_leaderboard(user):
    """
    Updates or creates leaderboard entry for a user based on TravelRecord.
    """
    total_countries = Country.objects.count()
    score = TravelRecord.objects.filter(user=user, visited=True).count()
    percentage = (score / total_countries * 100) if total_countries else 0

    leaderboard, _ = Leaderboard.objects.get_or_create(user=user)
    leaderboard.score = score
    leaderboard.total = total_countries
    leaderboard.percentage = percentage
    leaderboard.save(update_fields=["score", "total", "percentage"])


def calculate_ranks(queryset):
    """
    Sorts a leaderboard queryset and assigns rank.
    Returns a list of leaderboard objects with a 'rank' attribute.
    """
    sorted_qs = sorted(queryset, key=lambda x: (-x.percentage, -x.score))
    for idx, entry in enumerate(sorted_qs, start=1):
        entry.rank = idx
    return sorted_qs
