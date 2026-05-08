from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _ 
from core.models import BaseModel, State, City, Country
from django.core.mail import send_mail
from .validators import validate_cpf
import string
import random


username_validator = UnicodeUsernameValidator()

class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, username=None, **extra_fields):
        now = timezone.now()
        email = self.normalize_email(email)

        user = self.model(username=username, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True,
                                 **extra_fields)
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractUser, BaseModel):

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    full_name = models.CharField(_('full name'), max_length=60, null=True, blank=True)
    email = models.EmailField(_('email address'), blank=False, null=False, unique=True)
    username = models.CharField(
        "Username",
        max_length=150,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[username_validator],
        error_messages={"unique": "A user with that username already exists."},
    )
    cpf = models.CharField(_('CPF'), max_length=20, null=True, blank=True, unique=True, validators=[validate_cpf])
    birthdate = models.DateField(_('birth date'), null=True, blank=True)
    user_member_code = models.CharField(_('member code'), max_length=25, unique=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username",]

    objects = UserManager()

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def generate_user_member_code(self):
        char_set = string.digits + string.ascii_letters
        codigo = ''.join(random.sample(char_set*7, 7)).upper()
        return codigo

    def save(self, *args, **kwargs):
        self.user_member_code = self.generate_user_member_code()
        self.full_name = f"{self.first_name} {self.last_name}"
        super(User, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.full_name


class UserAddress(BaseModel):

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    CHOICE_ADDRESS_TYPE = (
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, blank=True, null=True)

    district = models.CharField(max_length=150, blank=True, null=True)
    street_address = models.CharField(max_length=150, blank=True, null=True)
    number = models.CharField(max_length=12, blank=True, null=True)
    address_type = models.CharField(max_length=10, choices=CHOICE_ADDRESS_TYPE, default='other', blank=True, null=True)
    complement = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.city} / {self.street_address} {self.number}"


class UserPhoneNumbers(BaseModel):

    class Meta:
        verbose_name = "Número de telefone"
        verbose_name_plural = "Números de telefone"

    CHOICE_PHONE_TYPE =(
        ('cell', 'Celular'),
        ('home', 'Casa'),
        ('work', 'Trabalho')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_type = models.CharField(max_length=10, choices=CHOICE_PHONE_TYPE, default='cell')
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    area_code = models.CharField(max_length=5)
    phone_number = models.CharField(max_length=17, unique=True)
    is_primary = models.BooleanField(default=False)