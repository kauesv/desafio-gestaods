from rest_framework import serializers
from .models import UserPoints, Nivel, UserPointsHistory, Award
from users.serializers import UserSerializer
from django.db import transaction
from django.utils import timezone


class NivelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nivel
        fields = "__all__"


class UserPointsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    nivel = NivelSerializer(read_only=True)

    class Meta:
        model = UserPoints
        fields = [
            "user",
            "total_points",
            "nivel",
            "points_to_next_tier",
            "lifetime_points_earned",
            "lifetime_points_redeemed",
        ]


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = "__all__"


class UserPointsHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    award = AwardSerializer(read_only=True)
    type_points_display = serializers.CharField(
        source="get_type_points_display",
        read_only=True
    )

    class Meta:
        model = UserPointsHistory
        fields = [
            "id",
            "user",
            "type_points",
            "type_points_display",
            "points",
            "award",
            "gain",
            "created_at",
            "updated_at",
        ]


class RedeemAwardSerializer(serializers.Serializer):
    pass

class RedeemAwardResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPointsHistory
        fields = (
            "id",
            "points",
            "type_points",
            "created_at",
        )