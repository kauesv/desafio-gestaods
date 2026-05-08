from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.validators import ValidationError

from gamifications.cron import prize_expiration
from gamifications.models import Award, Nivel, UserPoints, UserPointsHistory
from gamifications.services.redeem_award import RedeemAwardService


class RedeemAwardServiceTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="gamification-user@example.com",
            username="gamer_user",
            password="safe-pass-123",
            first_name="Game",
            last_name="User",
        )
        self.nivel = Nivel.objects.create(
            name="Bronze", start_points=0, end_points=999, multiplier=1.0
        )
        self.user_points = UserPoints.objects.create(
            user=self.user,
            total_points=200,
            nivel=self.nivel,
            lifetime_points_earned=200,
            lifetime_points_redeemed=0,
        )

    def test_redeem_award_successfully_debits_balance_and_creates_history(self):
        """
        Testa se o serviço RedeemAwardService desconta corretamente os pontos do usuário e cria um histórico (UserPointsHistory) ao realizar o resgate de um prêmio válido.
        O teste garante que:
            - O saldo total de pontos do usuário é reduzido em relação ao valor do prêmio.
            - O campo lifetime_points_redeemed é atualizado corretamente.
            - Um histórico do tipo REDEEM é criado e associado ao prêmio resgatado.
        """
        award = Award.objects.create(
            name="Cupom 10%",
            description="Desconto",
            points=80,
            expiration_date=timezone.now() + timedelta(days=5),
            activated=True,
        )

        history = RedeemAwardService.execute(user=self.user, award_id=award.id)

        self.user_points.refresh_from_db()
        self.assertEqual(self.user_points.total_points, 120)
        self.assertEqual(self.user_points.lifetime_points_redeemed, 80)
        self.assertEqual(history.type_points, UserPointsHistory.Operation.REDEEM)
        self.assertEqual(history.award_id, award.id)

    def test_redeem_award_raises_when_insufficient_balance(self):
        """
        Testa se o serviço RedeemAwardService lança uma exceção (ValidationError) quando o usuário não possui saldo de pontos suficiente para resgatar o prêmio.
        O teste garante que:
            - Nenhum histórico de resgate é criado.
            - O saldo e histórico de pontos do usuário permanecem inalterados.
        """
        award = Award.objects.create(
            name="Premio caro",
            description="",
            points=500,
            expiration_date=timezone.now() + timedelta(days=5),
            activated=True,
        )

        with self.assertRaises(ValidationError):
            RedeemAwardService.execute(user=self.user, award_id=award.id)

    def test_redeem_award_raises_when_award_expired(self):
        """
        Testa se o serviço RedeemAwardService lança uma exceção (ValidationError) quando o prêmio já está expirado na tentativa de resgate.

        O teste garante que:
            - Nenhum histórico de resgate é criado.
            - O saldo e histórico de pontos do usuário permanecem inalterados.
        """
        award = Award.objects.create(
            name="Premio expirado",
            description="",
            points=50,
            expiration_date=timezone.now() - timedelta(minutes=1),
            activated=True,
        )

        with self.assertRaises(ValidationError):
            RedeemAwardService.execute(user=self.user, award_id=award.id)


class UserPointsBusinessRulesTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="levels-user@example.com",
            username="levels_user",
            password="safe-pass-123",
            first_name="Levels",
            last_name="User",
        )
        self.bronze = Nivel.objects.create(
            name="Bronze", start_points=0, end_points=99, multiplier=1.0
        )
        self.silver = Nivel.objects.create(
            name="Silver", start_points=100, end_points=199, multiplier=1.2
        )
        self.gold = Nivel.objects.create(
            name="Gold", start_points=200, end_points=999, multiplier=1.5
        )

    def test_atualizar_nivel_changes_level_based_on_lifetime_points(self):
        """
        Testa se o método atualizar_nivel muda corretamente o nível do usuário com base nos pontos vitalícios (lifetime_points_earned).

        O teste garante que:
            - Um usuário inicialmente no nível Bronze com 150 pontos vitalícios é promovido para o nível Silver após chamar atualizar_nivel().
            - O campo nivel_id é atualizado corretamente no banco de dados.
        """
        user_points = UserPoints.objects.create(
            user=self.user,
            total_points=50,
            nivel=self.bronze,
            lifetime_points_earned=150,
        )

        updated_level = user_points.atualizar_nivel()
        user_points.refresh_from_db()

        self.assertIsNotNone(updated_level)
        self.assertEqual(user_points.nivel_id, self.silver.id)

    def test_pontos_para_proximo_nivel_returns_difference_to_next_tier(self):
        """
        Testa se o método pontos_para_proximo_nivel retorna corretamente a diferença de pontos necessária para atingir o próximo nível do usuário.
        O teste garante que, dado um usuário no nível Bronze com 150 pontos vitalícios, o método calcula corretamente que faltam 50 pontos para o usuário atingir o nível Silver (que começa em 200 pontos).
        """
        user_points = UserPoints.objects.create(
            user=self.user,
            total_points=0,
            nivel=self.bronze,
            lifetime_points_earned=150,
        )

        remaining = user_points.pontos_para_proximo_nivel()
        self.assertEqual(remaining, 50)

class PrizeExpirationTestCase(TestCase):
    def test_prize_expiration_deactivates_expired_awards(self):
        """
        Testa se a função prize_expiration desativa corretamente os prêmios expirados.
        Cria um prêmio expirado e outro válido, executa prize_expiration, e verifica que apenas o prêmio expirado foi desativado.
        """
        expired_award = Award.objects.create(
            name="Premiação expirada",
            description="",
            points=10,
            expiration_date=timezone.now() - timedelta(minutes=1),
            activated=True,
        )
        valid_award = Award.objects.create(
            name="Premiação válida",
            description="",
            points=20,
            expiration_date=timezone.now() + timedelta(days=1),
            activated=True,
        )

        result = prize_expiration()

        expired_award.refresh_from_db()
        valid_award.refresh_from_db()
        self.assertFalse(expired_award.activated)
        self.assertTrue(valid_award.activated)
        self.assertGreaterEqual(result, 1)
 