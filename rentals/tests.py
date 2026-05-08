from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from gamifications.models import (
    CarPoints,
    DaysPoints,
    DefaultPoints,
    Nivel,
    UserPoints,
    UserPointsHistory,
)
from rentals.models import Car, Rental
from rentals.utils import calculate_discount, calculate_late_fee
from rentals.views import create_rental, return_rental


class RentalBusinessRulesTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="rental-user@example.com",
            username="rental_user",
            password="safe-pass-123",
            first_name="Rental",
            last_name="User",
        )
        self.car = Car.objects.create(
            brand="Toyota",
            model="Corolla",
            year=2022,
            category=Car.Operation.STANDARD,
            daily_rate=100.0,
            available=True,
        )

    def _create_open_rental(self, days=5):
        start_date = timezone.now() - timedelta(days=1)
        end_date = start_date + timedelta(days=days)
        return Rental.objects.create(
            car=self.car,
            user=self.user,
            start_date=start_date,
            end_date=end_date,
            total_cost=Decimal("500.00"),
            returned=False,
        )

    def test_cannot_revert_returned_flag_from_true_to_false(self):
        """Testa se não é possível reverter o campo 'returned' de True para False após devolução do carro."""
        rental = self._create_open_rental()
        rental.returned = True
        rental.save()

        rental.refresh_from_db()
        self.assertTrue(rental.returned)

        rental.returned = False
        with self.assertRaises(ValidationError):
            rental.save()

    def test_sets_actual_return_date_when_marked_as_returned(self):
        """Testa se a data de devolução real é definida ao marcar o aluguel como devolvido."""
        rental = self._create_open_rental()
        self.assertIsNone(rental.actual_return_date)

        rental.returned = True
        rental.save()

        rental.refresh_from_db()
        self.assertIsNotNone(rental.actual_return_date)

    def test_return_transition_applies_points_and_creates_history(self):
        """Este teste verifica se ao realizar a devolução de um aluguel, os pontos são corretamente aplicados ao usuário e o histórico de pontuação é criado."""
        Nivel.objects.create(name="Bronze", start_points=0, end_points=999, multiplier=1.0)
        DefaultPoints.objects.create(
            name="Diarios", type_points=DefaultPoints.Operation.DAILY_POINTS, points=10
        )
        DefaultPoints.objects.create(
            name="Devolucao", type_points=DefaultPoints.Operation.RETURN_POINTS, points=30
        )
        CarPoints.objects.create(
            name="Standard Bonus", category_car=Car.Operation.STANDARD, points=2
        )
        DaysPoints.objects.create(name="Faixa 5 dias", points=7, start_date=5, end_date=5)

        start_date = timezone.now() - timedelta(days=2)
        end_date = start_date + timedelta(days=5)
        rental = Rental.objects.create(
            car=self.car,
            user=self.user,
            start_date=start_date,
            end_date=end_date,
            total_cost=Decimal("500.00"),
            returned=False,
        )

        rental.returned = True
        rental.actual_return_date = start_date + timedelta(days=3)
        rental.save()

        user_points = UserPoints.objects.get(user=self.user)
        self.assertEqual(user_points.total_points, 97)
        self.assertEqual(user_points.lifetime_points_earned, 97)

        history = UserPointsHistory.objects.filter(user=self.user).latest("created_at")
        self.assertEqual(history.type_points, UserPointsHistory.Operation.EARN)
        self.assertEqual(history.points, 97)
        self.assertTrue(any(item.get("type") == "return_points" for item in history.gain))


class RentalsViewBusinessRulesTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(
            email="view-user@example.com",
            username="view_user",
            password="safe-pass-123",
        )

    @patch("rentals.views.RentalSerializer")
    @patch("rentals.views.database.update_car")
    @patch("rentals.views.Rental.objects.create")
    @patch("rentals.views.database.get_car_by_id")
    def test_create_rental_applies_5_percent_discount_for_more_than_3_days(
        self,
        mock_get_car,
        mock_rental_create,
        mock_update_car,
        mock_rental_serializer,
    ):
        """
        Esta função testa se a view `create_rental` aplica corretamente o desconto de 5% quando uma locação é criada para mais de 3 dias.
        Ela utiliza mocks para isolar a lógica de desconto, criando um aluguel de 5 dias e verificando se o valor total foi aplicado corretamente.
        """
        car = SimpleNamespace(id=1, daily_rate=100.0, available=True)
        mock_get_car.return_value = car
        mock_rental_create.return_value = SimpleNamespace(id=123)
        mock_rental_serializer.return_value.data = {"id": 123}

        request = self.factory.post(
            "/v1/rentals/create",
            {
                "car_id": 1,
                "days": 5,
            },
            format="json",
        )
        force_authenticate(request, user=self.user)

        response = create_rental(request)

        self.assertEqual(response.status_code, 201)
        called_total_cost = mock_rental_create.call_args.kwargs["total_cost"]
        self.assertEqual(called_total_cost, Decimal("475.00"))
        self.assertEqual(mock_rental_create.call_args.kwargs["user"], self.user)
        self.assertFalse(car.available)
        mock_update_car.assert_called_once()

    @patch("rentals.views.RentalSerializer")
    @patch("rentals.views.database.update_car")
    @patch("rentals.views.database.update_rental")
    @patch("rentals.views.database.get_rental_by_id")
    def test_return_rental_applies_late_fee_when_returned_after_end_date(
        self,
        mock_get_rental,
        mock_update_rental,
        mock_update_car,
        mock_rental_serializer,
    ):
        """
        Essa função testa se a view `return_rental` aplica corretamente a multa por atraso quando um carro é devolvido após a data final da locação.
        O teste simula a devolução de um aluguel com atraso e verifica se a multa (`late_fee`) é calculada, atribuída e somada ao valor total, além de garantir que o carro é marcado como disponível novamente.
        """
        late_end_date = timezone.now() - timedelta(days=2)
        car = SimpleNamespace(daily_rate=100.0, available=False)
        rental = SimpleNamespace(
            id=1,
            returned=False,
            end_date=late_end_date,
            total_cost=Decimal("300.00"),
            late_fee=None,
            car=car,
            actual_return_date=None,
        )

        mock_get_rental.return_value = rental
        mock_rental_serializer.return_value.data = {"id": 1}

        request = self.factory.post("/v1/rentals/1/return", {}, format="json")
        response = return_rental(request, rental_id=1)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(rental.late_fee)
        self.assertGreater(rental.late_fee, Decimal("0"))
        self.assertTrue(car.available)
        mock_update_rental.assert_called_once()
        mock_update_car.assert_called_once()


class RentalsUtilsBusinessRulesTestCase(TestCase):
    def test_calculate_discount_returns_10_percent_for_more_than_7_days(self):
        """
        Essa função testa se a função `calculate_discount` retorna corretamente 10% de desconto para alugueis com mais de 7 dias. 
        O teste garante que para 8 dias e valor base 1000.0, o valor do desconto é 100.0.
        """
        discount = calculate_discount(8, 1000.0)
        self.assertEqual(discount, 100.0)

    def test_calculate_discount_returns_5_percent_for_more_than_3_days(self):
        """
        Essa função testa se a função `calculate_discount` retorna corretamente 5% de desconto para alugueis com mais de 3 dias.
        O teste garante que para 5 dias e valor base 1000.0, o valor do desconto é 50.0.
        """
        discount = calculate_discount(5, 1000.0)
        self.assertEqual(discount, 50.0)

    def test_calculate_late_fee_uses_1_point_5_multiplier(self):
        """
        Essa função testa se a função `calculate_late_fee` utiliza corretamente o multiplicador de 1.5 sobre a diária e a quantidade de dias de atraso.
        O teste garante que, para 2 dias de atraso e diária de 100, a multa calculada deve ser 300.0.
        """
        fee = calculate_late_fee(2, 100)
        self.assertEqual(fee, 300.0)
