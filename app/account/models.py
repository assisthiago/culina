import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from app.api import NominatimAPI, ViaCEPAPI
from app.utils import SoftDeleteModel, TimestampedModel, bounding_box, haversine_km


class Account(TimestampedModel, SoftDeleteModel):

    TYPE_CLIENT = "client"
    TYPE_ADMIN = "admin"
    TYPE_CHOICES = (
        (TYPE_CLIENT, "Cliente"),
        (TYPE_ADMIN, "Administrador"),
    )

    # Relations
    user = models.OneToOneField(
        User,
        verbose_name="usuário",
        related_name="account",
        on_delete=models.CASCADE,
    )

    # Fields
    uuid = models.CharField(verbose_name="UUID", unique=True, max_length=36)
    type = models.CharField(
        verbose_name="tipo",
        max_length=10,
        choices=TYPE_CHOICES,
    )
    cpf = models.CharField(verbose_name="CPF", unique=True, max_length=11)
    phone = models.CharField(verbose_name="telefone", unique=True, max_length=13)

    class Meta:
        verbose_name = "conta"
        verbose_name_plural = "contas"
        db_table = "account"

    def __str__(self):
        return self.user.get_full_name()
