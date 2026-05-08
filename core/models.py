from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _ 
from unidecode import unidecode


class BaseModel(models.Model):

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    created_at = models.DateTimeField(verbose_name="Criado às", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Atualizado às", auto_now=True)
    deleted_at = models.DateTimeField(
        verbose_name="Deletado às", blank=True, null=True, default=None
    )
    deleted = models.BooleanField(verbose_name="Deletado", default=False, db_index=True)

    def delete(self, force=False):
        if force:
            return super().delete()

        self.deleted = True
        self.deleted_at = timezone.now()
        self.save()


class Country(BaseModel):

    class Meta:
        verbose_name = _("País")
        verbose_name_plural = _("Países")

    name = models.CharField(max_length=100, unique=True)
    name_without_accents = models.CharField(max_length=180)
    alpha_code = models.CharField(max_length=3, unique=True, blank=True, null=True)
    country_code = models.CharField(max_length=5, unique=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    sub_region = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.name_without_accents = unidecode(self.name.lower())
        super(Country, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class State(BaseModel):

    class Meta:
        verbose_name = _("Estado")
        verbose_name_plural = _("Estados")

    name = models.CharField(max_length=180)
    name_without_accents = models.CharField(max_length=180)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    uf = models.CharField(max_length=2)
    cod = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        self.name_without_accents = unidecode(self.name.lower())
        super(State, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.name


class City(BaseModel):

    class Meta:
        verbose_name = _("Município")
        verbose_name_plural = _("Municípios")

    name = models.CharField(max_length=180)
    name_without_accents = models.CharField(max_length=180)
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    cod = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        self.name_without_accents = unidecode(self.name.lower())
        super(City, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name