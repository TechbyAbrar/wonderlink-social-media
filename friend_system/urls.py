from django.urls import path
from .views import (
    SendFollowRequestAPIView,
    AcceptFollowRequestAPIView,
    RejectFollowRequestAPIView,
    FollowBackAPIView,
    FollowersListAPIView,
    FollowingListAPIView,
    ProfileAPIView, SearchUserAPIView, ReportUserAPIView, BlockUserAPIView, BlockListAPIView, PendingFollowRequestsAPIView, FriendsListAPIView
)

urlpatterns = [
    path('follow/send/', SendFollowRequestAPIView.as_view(), name='send-follow-request'),
    path('follow-accept/<int:follow_id>/', AcceptFollowRequestAPIView.as_view(), name='accept-follow-request'),
    path('follow-reject/<int:follow_id>/', RejectFollowRequestAPIView.as_view(), name='reject-follow-request'),
    path('follow-followback/<int:user_id>/', FollowBackAPIView.as_view(), name='follow-back'),
    path('user/followers/<int:user_id>/', FollowersListAPIView.as_view(), name='user-followers'),
    path('user/following/<int:user_id>/', FollowingListAPIView.as_view(), name='user-following'),
    path('user/profile/<int:user_id>/', ProfileAPIView.as_view(), name='user-profile'),
    path('search/users/', SearchUserAPIView.as_view(), name='search-users'),
    # report and block endpoints
    path("report/", ReportUserAPIView.as_view(), name="report-user"),
    path("block/", BlockUserAPIView.as_view(), name="block-user"),
    path("block/list/", BlockListAPIView.as_view(), name="blocked-list"),
    #follow requests pending
    path('follow-requests/pending/', PendingFollowRequestsAPIView.as_view(), name='pending-follow-requests'),
    #mutual friends
    path('friends-list/', FriendsListAPIView.as_view(), name='friends-list'),
]


