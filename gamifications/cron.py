from gamifications.models import *
from django.utils import timezone


def prize_expiration():
    """
    Procura todos os prêmios expirados e desativa.
    Retorna a quantidade de registros atualizados.
    """

    now = timezone.now()

    expired_prizes = Award.objects.filter(
        activated=True,
        expiration_date__isnull=False,
        expiration_date__lt=now
    )

    updated_quantity = expired_prizes.update(activated=False)
    print(f"{updated_quantity} prêmios foram desativados.")

    return updated_quantity