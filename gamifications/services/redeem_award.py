from gamifications.models import UserPoints, UserPointsHistory, Award
from django.db import transaction
from django.utils import timezone
from rest_framework.validators import ValidationError


class RedeemAwardService:
    @classmethod
    def execute(cls, *, user, award_id):
        with transaction.atomic():

            user_points = (
                UserPoints.objects
                .select_for_update()
                .get(user=user)
            )

            award = (
                Award.objects
                .select_for_update()
                .filter(id=award_id)
                .first()
            )

            if not award:
                raise ValidationError({"message": "Prêmio não encontrado."})

            if not award.activated:
                raise ValidationError({"message": "Prêmio inativo."})

            if award.expiration_date <= timezone.now():
                raise ValidationError({"message": "Prêmio expirado."})

            if user_points.total_points < award.points:
                raise ValidationError({"message": "Saldo insuficiente."})
           

            user_points.total_points -= award.points
            user_points.lifetime_points_redeemed += award.points
            user_points.save()

            return UserPointsHistory.objects.create(
                user=user,
                type_points=UserPointsHistory.Operation.REDEEM,
                points=award.points,
                award=award,
                gain=[],
            )