from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from .models import Leaderboard
from .serializers import LeaderboardSerializer
from .utils import calculate_ranks
from friend_system.models import Follow


class GlobalLeaderboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            qs = Leaderboard.objects.select_related("user")
            ranked = calculate_ranks(qs)
            serializer = LeaderboardSerializer(ranked, many=True)
            return Response({
                "success": True,
                "message": "Global leaderboard fetched successfully.",
                "data": {"global_leaderboard": serializer.data}
            })
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Error fetching leaderboard: {str(e)}",
                "data": {"global_leaderboard": []}
            }, status=500)


class FriendsLeaderboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            # Mutual friends: both sides accepted
            # Get IDs of users who accepted the current user
            accepted_by = Follow.objects.filter(receiver=user, status="accepted").values_list("requester_id", flat=True)
            # Get IDs of users whom the current user accepted
            accepted_users = Follow.objects.filter(requester=user, status="accepted").values_list("receiver_id", flat=True)
            # Mutual friends = intersection
            mutual_ids = set(accepted_by).intersection(set(accepted_users))

            if not mutual_ids:
                return Response({
                    "success": True,
                    "message": "No friends found for leaderboard.",
                    "data": {"friends_leaderboard": []}
                })

            qs = Leaderboard.objects.filter(user__id__in=mutual_ids).select_related("user")
            ranked = calculate_ranks(qs)
            serializer = LeaderboardSerializer(ranked, many=True)
            return Response({
                "success": True,
                "message": "Friends leaderboard fetched successfully.",
                "data": {"friends_leaderboard": serializer.data}
            })
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Error fetching friends leaderboard: {str(e)}",
                "data": {"friends_leaderboard": []}
            }, status=500)

            
            
# Dashboard

from rest_framework.permissions import IsAdminUser
from django.db.models import Count
from django.db.models.functions import TruncMonth
from collections import OrderedDict
from accounts.models import UserAuth, TravelRecord
from locations.models import Country
from .serializers import DashboardSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncMonth
from collections import OrderedDict
from accounts.models import UserAuth
from locations.models import Country, TravelRecord
from .serializers import DashboardSerializer

class AdminDashboardAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = {
            "total_users": self.get_total_users(),
            "new_users_by_month": self.get_new_users_by_month(),
            "total_travelled_users": self.get_total_travelled_users(),
            "user_growth_by_month": self.get_user_growth_by_month(),
            "most_visited_countries": self.get_most_visited_countries()
        }
        serializer = DashboardSerializer(data)
        return Response({"success": True, "message": "Dashboard data fetched successfully.", "data": serializer.data})

    # -------------------- Helpers --------------------
    def get_total_users(self):
        return UserAuth.objects.count()

    def get_new_users_by_month(self):
        queryset = (
            UserAuth.objects
            .annotate(month=TruncMonth('date_joined'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        return OrderedDict(
            [(q['month'].strftime('%Y-%m'), q['count']) for q in queryset]
        )

    def get_total_travelled_users(self):
        return TravelRecord.objects.filter(visited=True).values('user').distinct().count()

    def get_user_growth_by_month(self):
        monthly_counts = self.get_new_users_by_month()
        cumulative = OrderedDict()
        total = 0
        for month, count in monthly_counts.items():
            total += count
            cumulative[month] = total
        return cumulative

    def get_most_visited_countries(self, top_n=5):
        # Step 1: Get country_codes with visit counts
        queryset = (
            TravelRecord.objects.filter(visited=True)
            .values('country__country_code')
            .annotate(visits=Count('id'))
            .order_by('-visits')[:top_n]
        )

        # Step 2: Map codes to display names
        country_codes = [q['country__country_code'] for q in queryset]
        countries = Country.objects.filter(country_code__in=country_codes)
        country_map = {c.country_code: c.get_country_code_display() for c in countries}

        # Step 3: Build final list
        result = []
        for q in queryset:
            code = q['country__country_code']
            result.append({
                "country_code": code,
                "country_name": country_map.get(code, code),
                "visits": q['visits']
            })
        return result


from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import F
from locations.models import Country
from locations.country_choices import COUNTRY_CHOICES  # <-- import your list

class ALLCountryListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        # Convert your COUNTRY_CHOICES list to a dict for fast lookup
        country_code_map = dict(COUNTRY_CHOICES)

        # Fetch only required fields as dictionaries
        countries = Country.objects.select_related("continent").annotate(
            continent_name=F("continent__name")
        ).values(
            "country_code",
            "capital",
            "region",
            "continent_name",
            "official_language",
            "population",
            "status"
        )

        # Build response data
        data = [
            {
                "country_code": c["country_code"],
                "country_name": country_code_map.get(c["country_code"], c["country_code"]),
                "capital": c["capital"],
                "region": c["region"],
                "continent": c["continent_name"],
                "official_language": c["official_language"],
                "population": c["population"],
                "status": c["status"]
            }
            for c in countries
        ]

        return Response({
            "success": True,
            "message": "Countries fetched successfully",
            "data": data
        })
