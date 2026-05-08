from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import UserPoints, UserPointsHistory
from .serializers import UserPointsSerializer, UserPointsHistorySerializer, RedeemAwardResponseSerializer
from .serializers import RedeemAwardSerializer
from .services.redeem_award import RedeemAwardService

class UserPointsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user_points = UserPoints.objects.select_related(
                "user",
                "nivel"
            ).get(user_id=user_id)

            serializer = UserPointsSerializer(user_points)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except UserPoints.DoesNotExist:
            return Response(
                {"detail": "Pontuação do usuário não encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )


class UserPointsHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        history = UserPointsHistory.objects.select_related(
            "user",
            "award"
        )

        if user_id:
            history = history.filter(user_id=user_id)

        history = history.order_by("-created_at")

        serializer = UserPointsHistorySerializer(history, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class RedeemAwardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, award_id):

        serializer = RedeemAwardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        history = RedeemAwardService.execute(
            user=request.user,
            award_id=award_id,
        )

        response_serializer = RedeemAwardResponseSerializer(history)

        return Response(
            {
                "message": "Prêmio resgatado com sucesso.",
                "data": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )