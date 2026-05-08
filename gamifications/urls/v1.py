from django.urls import path, include
from rest_framework import routers
from gamifications.views import UserPointsAPIView, UserPointsHistoryAPIView, RedeemAwardView

app_name = 'gamifications'

router = routers.DefaultRouter()

urlpatterns = [
    path(
        "user-points/<int:user_id>/",
        UserPointsAPIView.as_view(),
        name="user-points",
    ),
    path(
        "user-points/history/",
        UserPointsHistoryAPIView.as_view(),
        name="user-points-history",
    ),
    path(
        "user-points/<int:user_id>/history",
        UserPointsHistoryAPIView.as_view(),
        name="user-points-history-by-user",
    ),
    path(
        "awards/<int:award_id>/redeem/",
        RedeemAwardView.as_view(),
        name="redeem-award",
    ),
]