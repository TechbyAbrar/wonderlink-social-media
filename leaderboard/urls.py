# leaderboard/urls.py
from django.urls import path
from .views import GlobalLeaderboardAPIView, FriendsLeaderboardAPIView, AdminDashboardAPIView, ALLCountryListAPIView

urlpatterns = [
    path("global/", GlobalLeaderboardAPIView.as_view(), name="global-leaderboard"),
    path("friends/", FriendsLeaderboardAPIView.as_view(), name="friends-leaderboard"),
    path('admin/dashboard/', AdminDashboardAPIView.as_view(), name='admin-dashboard'),
    path('dashboard/all-countries/', ALLCountryListAPIView.as_view(), name='all-countries'),
]
