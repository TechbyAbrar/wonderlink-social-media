from django.urls import path
from .views import (CountryListAPIView, CountryByCodeAPIView, CountryUpdateAPIView,
                    UserTravelStats, GetAllContinentsAPIView, PublicTravelRecordListAPIView,
                    MyTravelRecordCreateAPIView, SearchCountryAPIView,
                    GlobalFeedAPIView, FriendsFeedAPIView)

urlpatterns = [
    path("all-countries/", CountryListAPIView.as_view(), name="country-list"),
    path("countries/<str:code>/", CountryByCodeAPIView.as_view(), name="country-by-code"),
    path("country/manage/<str:code>/",CountryUpdateAPIView.as_view(),name="country-update-delete"),
    path('api/user/travel-stats/<int:user_id>', UserTravelStats.as_view(), name='user_travel_stats'),
    path('all-continents/', GetAllContinentsAPIView.as_view(), name='continent-list'),
    path('travel-records/', PublicTravelRecordListAPIView.as_view(), name='travel-record-list'),
    path('my/travel-records/create/', MyTravelRecordCreateAPIView.as_view(), name='travel-record-create'),
    path('my/travel-records/update/<int:pk>/', MyTravelRecordCreateAPIView.as_view(), name='travel-record-create'),
    path('search-countries/', SearchCountryAPIView.as_view(), name='search-countries'),
    # feed
    path("feed/global/", GlobalFeedAPIView.as_view(), name="global-feed"),
    path("feed/friends/", FriendsFeedAPIView.as_view(), name="friends-feed"),
]

