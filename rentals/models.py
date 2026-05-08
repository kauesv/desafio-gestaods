from django.db import models
from django.core.validators import MinValueValidator, EmailValidator
from django.conf import settings
from core.models import BaseModel
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone

class Car(BaseModel):
    """
    Modelo de Carro representando veículos disponíveis para locação
    """

    class Meta:
        verbose_name = "Carro"
        verbose_name_plural = "Carros"
        ordering = ['brand', 'model']
    class Operation(models.TextChoices):
        ECONOMICOS = "economicos", "Econômicos"
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"

    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField(validators=[MinValueValidator(1900)])
    category = models.CharField(max_length=10, choices=Operation.choices, null=False, blank=False)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"


class Rental(BaseModel):
    """
    Modelo de Aluguel representando o registro de locações de veículos por clientes.
    """

    class Meta:
        verbose_name = "Aluguel"
        verbose_name_plural = "Aluguéis"
        ordering = ['-created_at']

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='rentals')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    returned = models.BooleanField(default=False)
    actual_return_date = models.DateTimeField(null=True, blank=True)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Rental.objects.get(pk=self.pk)

            # Impede voltar de True -> False
            if old_instance.returned and not self.returned:
                raise ValidationError(
                    {"message": "Não é permitido desfazer uma devolução."}
                )

            # Detecta mudança de False -> True
            if not old_instance.returned and self.returned:
                self.actual_return_date = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Rental {self.id} - {self.user}"


@receiver(pre_save, sender=Rental)
def track_returned_change(sender, instance, **kwargs):
    """Guarda o valor antigo de returned antes de salvar."""
    if instance.pk:
        old_instance = Rental.objects.get(pk=instance.pk)
        instance._old_returned = old_instance.returned
    else:
        instance._old_returned = False


@receiver(post_save, sender=Rental)
def rental_returned(sender, instance, **kwargs):
    """
    Executa ações relacionadas à gamificação sempre que o campo 'returned' de um aluguel muda de False para True.
    Calcula e aplica a pontuação ao usuário com base nos critérios definidos.
    """
    if kwargs.get('created'):
        return

    old_returned = getattr(instance, '_old_returned', False)

    if not (old_returned is False and instance.returned is True):
        return

    from gamifications.models import (
        DefaultPoints,
        CarPoints,
        DaysPoints,
        UserPoints,
        UserPointsHistory,
        Nivel
    )

    # Dias contratados
    contracted_rental_days = (instance.end_date - instance.start_date).days

    # Obtem os pontos default
    default_points = {
        item.type_points: item.points
        for item in DefaultPoints.objects.filter(
            type_points__in=["daily_points", "return_points"]
        )
    }

    # Pontos base (Apenas o Contratado)
    daily_points = default_points.get("daily_points", 0) * contracted_rental_days

    # Bônus carro (Apenas o Contratado)
    car_points_obj = CarPoints.objects.filter(category_car=instance.car.category).first()
    car_points = (car_points_obj.points if car_points_obj else 0) * contracted_rental_days

    # Bônus por dias locação (Apenas o Contratado)
    days_points_obj = DaysPoints.objects.filter(
        start_date__lte=contracted_rental_days,
        end_date__gte=contracted_rental_days,
    ).first()
    days_points = days_points_obj.points if days_points_obj else 0

    # Soma dos pontos
    points = daily_points + car_points + days_points

    # Definição do metadados
    histories = [
        {"type": "daily_points", "points": daily_points},
        {"type": "CarPoints", "points": car_points},
        {"type": "DaysPoints", "points": days_points},
    ]

    # Bônus devolução pontual (A Data real de devolução)
    if (
        instance.actual_return_date
        and instance.start_date <= instance.actual_return_date <= instance.end_date
    ):
        return_points = default_points.get("return_points", 0)
        points += return_points
        histories.append({
            "type": "return_points",
            "points": return_points,
        })

    # obtem usuario, se não cria.
    nivel_inicial = Nivel.objects.filter(start_points=0).first()

    user_points, _ = UserPoints.objects.get_or_create(
        user=instance.user,
        defaults={
            "total_points": 0,
            "nivel": nivel_inicial,
            "points_to_next_tier": 0,
            "lifetime_points_earned": 0,
            "lifetime_points_redeemed": 0,
        },
    )

    # Multiplicador
    multiplicador = user_points.nivel.multiplier if user_points.nivel else 1
    final_points = round(points * multiplicador)
    histories.append({
        "multiplier": multiplicador,
        "final_score": final_points
    })

    # Registra os pontos do usuário e atualização de nivel
    user_points.total_points += final_points
    user_points.lifetime_points_earned += final_points

    user_points.atualizar_nivel()
    user_points.points_to_next_tier = user_points.pontos_para_proximo_nivel()

    user_points.save()

    # Auditoria (Historico)
    UserPointsHistory.objects.create(
        user=instance.user,
        type_points=UserPointsHistory.Operation.EARN,
        points=final_points,
        gain=histories,
    )