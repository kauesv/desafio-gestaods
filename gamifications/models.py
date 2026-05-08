from email.policy import default
from django.db import models
from core.models import BaseModel
from rentals.models import Car
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

class DefaultPoints(BaseModel):
    """Armazena configurações padrão de pontuação do sistema de gamificação."""

    class Meta:
        verbose_name = "Ponto Padrão"
        verbose_name_plural = "Pontos Padrões"

    class Operation(models.TextChoices):
        DAILY_POINTS = "daily_points", "Pontos Diários"
        RETURN_POINTS = "return_points", "Pontos por devolução"

    name = models.CharField(max_length=100, null=False, blank=False)
    type_points = models.CharField(max_length=20,choices=Operation.choices, null=False, blank=False)
    points = models.PositiveIntegerField(null=False, blank=False)

    def __str__(self):
        return f"{self.get_type_points_display()}"

class CarPoints(BaseModel):
    """Armazena pontuação específica para cada carro."""

    class Meta:
        verbose_name = "Ponto por carro"
        verbose_name_plural = "Pontos por carros"

    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    category_car = models.CharField(max_length=10, choices=Car.Operation.choices, null=False, blank=False)
    points = models.PositiveIntegerField(null=False, blank=False, default=0)
    activated = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.category_car}"

class DaysPoints(BaseModel):
    """Pontuação conforme a duração do aluguel."""

    class Meta:
        verbose_name = "Ponto por duração"
        verbose_name_plural = "Pontos por duração"

    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    points = models.PositiveIntegerField(null=False, blank=False, default=0)
    start_date = models.PositiveIntegerField(null=False, blank=False, default=0)
    end_date = models.PositiveIntegerField(null=False, blank=False, default=0)
    activated = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.start_date} a {self.end_date}"

class Nivel(BaseModel):
    """Multiplicador de pontos por nível do usuário."""

    class Meta:
        verbose_name = "Nível"
        verbose_name_plural = "Níveis"

    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    start_points = models.PositiveIntegerField(null=False, blank=False, default=0)
    end_points = models.PositiveIntegerField(null=False, blank=False, default=0)
    multiplier = models.FloatField(null=False, blank=False)

    def __str__(self):
        return f"{self.name} - {self.multiplier}"

class Award(BaseModel):
    """Prêmios disponíveis para os usuários."""

    class Meta:
        verbose_name = "Prêmio"
        verbose_name_plural = "Prêmios"

    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    points = models.PositiveIntegerField(null=False, blank=False, default=0)
    expiration_date = models.DateTimeField(null=False, blank=False)
    activated = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.points}"


class UserPoints(BaseModel):
    """Armazena o saldo de pontos do usuário."""

    class Meta:
        verbose_name = "Ponto do Usuário"
        verbose_name_plural = "Pontos dos Usuários"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False)
    total_points = models.PositiveIntegerField(null=False, blank=False, default=0)
    nivel = models.ForeignKey(Nivel, on_delete=models.SET_NULL, null=True)
    points_to_next_tier = models.PositiveIntegerField(null=False, blank=False, default=0)
    lifetime_points_earned = models.PositiveIntegerField(null=False, blank=False, default=0)
    lifetime_points_redeemed = models.PositiveIntegerField(null=False, blank=False, default=0)

    def atualizar_nivel(self):
        nivel = Nivel.objects.filter(
            start_points__lte=self.lifetime_points_earned,
            end_points__gte=self.lifetime_points_earned,
        ).first()

        if not nivel:
            return None

        if self.nivel_id != nivel.id:
            self.nivel = nivel
            self.save(update_fields=["nivel"])

        return nivel

    def pontos_para_proximo_nivel(self):
        proximo_nivel = Nivel.objects.filter(
            start_points__gt=self.lifetime_points_earned
        ).order_by("start_points").first()

        if not proximo_nivel:
            return 0

        return max(proximo_nivel.start_points - self.lifetime_points_earned, 0)

    def __str__(self):
        return f"{self.user} - {self.nivel}"

class UserPointsHistory(BaseModel):
    """Registro das transações de pontos dos usuários."""

    class Meta:
        verbose_name = "Histórico de ponto do usuário"
        verbose_name_plural = "Histórico de pontos dos usuários"

    class Operation(models.TextChoices):
        EARN = "earn", "Ganho"
        REDEEM = "redeem", "Resgate"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False)
    type_points = models.CharField(max_length=10, choices=Operation.choices, null=False, blank=False)
    points = models.PositiveIntegerField(null=False, blank=False)
    award = models.ForeignKey(
        Award,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Preenchido quando o tipo for resgate.",
    )
    gain = models.JSONField(default=list, null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.type_points} - {self.points} pontos"


class ExportHistoricalPointsCSV(BaseModel):
    """Model de exportação do histórico de pontos dos usuários"""

    class Meta:
        verbose_name = "Exporta o histórico de ponto"
        verbose_name_plural = "Exporta o histórico de pontos"
        ordering = ['-id']

    file = models.FileField(
        upload_to="gamifications/relatorios/", null=True, blank=True)
    start_date =  models.DateTimeField(null=False, blank=False)
    end_date = models.DateTimeField(null=False, blank=False)
    generated_successfully = models.BooleanField(
        default=False, null=True, blank=True)

    def __str__(self):
       return f"{self.file} / {self.generated_successfully}"


@receiver(post_save, sender=ExportHistoricalPointsCSV)
def export_history_csv_task(sender, instance, **kwargs):
    """Chama o processo que vai gerar o arquivo CSV"""
    from gamifications.services_csv import ExportHistoricalPointsCSVService

    created = kwargs.get('created')
    if created:
        service = ExportHistoricalPointsCSVService(instance)
        try:
            instance.generated_successfully = service.handle()
        except Exception as err:
            print('ERRO: ' + str(err))
            instance.generated_successfully = False
        instance.save(update_fields=["generated_successfully"])