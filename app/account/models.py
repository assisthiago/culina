import re

from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Q

from app.utils import BaseModel


class Account(BaseModel):

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

    def save(self, *args, **kwargs):
        # Ensure the related user is staff if account type is admin
        if self.type == self.TYPE_ADMIN:
            self.user.is_staff = True
            self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name()

    def format_cpf(self):
        return re.sub(r"(\d{3})(\d{3})(\d{3})(\d{2})", r"\1.\2.\3-\4", self.cpf)

    def format_phone(self):
        return re.sub(r"(\d{2})(\d{5})(\d{4})", r"(\1) \2-\3", self.phone)


class Address(BaseModel):

    # Relations
    account = models.ForeignKey(
        Account,
        verbose_name="conta",
        related_name="addresses",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    store = models.ForeignKey(
        "store.Store",
        verbose_name="loja",
        related_name="addresses",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # Fields
    label = models.CharField(
        verbose_name="rótulo",
        max_length=50,
        null=True,
        blank=True,
        help_text="Ex: Casa, Trabalho, Matriz, Filial",
    )
    is_default = models.BooleanField(
        verbose_name="padrão",
        default=False,
        help_text="Endereço principal.",
    )
    zip_code = models.CharField(
        verbose_name="CEP",
        db_index=True,
        max_length=8,
    )

    # Fields from ViaCEP
    street = models.CharField(verbose_name="logradouro", max_length=255)
    number = models.CharField(verbose_name="número", max_length=20)
    neighborhood = models.CharField(verbose_name="bairro", max_length=255)
    complement = models.CharField(
        verbose_name="complemento",
        max_length=255,
        null=True,
        blank=True,
    )
    reference = models.CharField(
        verbose_name="referência",
        max_length=255,
        null=True,
        blank=True,
    )
    city = models.CharField(verbose_name="cidade", max_length=255)
    state = models.CharField(verbose_name="UF", max_length=2)

    # Fields from geocoding via NominatimAPI
    latitude = models.DecimalField(
        verbose_name="latitude",
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        db_index=True,
    )
    longitude = models.DecimalField(
        verbose_name="longitude",
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        verbose_name = "endereço"
        verbose_name_plural = "endereços"
        db_table = "address"
        constraints = [
            # XOR: Address belongs to either Account or Store
            models.CheckConstraint(
                condition=(
                    (Q(account__isnull=False) & Q(store__isnull=True))
                    | (Q(account__isnull=True) & Q(store__isnull=False))
                ),
                name="address_owner_xor_account_store",
            ),
            # Brazilian zip code format: 8 digits
            models.CheckConstraint(condition=Q(zip_code__regex=r"^\d{8}$"), name="address_zipcode_8_digits"),
            models.CheckConstraint(condition=Q(state__regex=r"^[A-Z]{2}$"), name="address_state_uf_format"),
            # One default per Account (when address belongs to account)
            models.UniqueConstraint(
                fields=["account"],
                condition=Q(is_default=True) & Q(account__isnull=False),
                name="unique_default_address_per_account",
            ),
            # One default per Store (when address belongs to store)
            models.UniqueConstraint(
                fields=["store"],
                condition=Q(is_default=True) & Q(store__isnull=False),
                name="unique_default_address_per_store",
            ),
        ]

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # If setting this address as default, unset other default addresses for the same owner
            if self.is_default:
                qs = Address.objects.select_for_update().filter(is_default=True)
                if self.account_id:
                    qs = qs.filter(account_id=self.account_id, store__isnull=True)
                elif self.store_id:
                    qs = qs.filter(store_id=self.store_id, account__isnull=True)
                if self.pk:
                    qs = qs.exclude(pk=self.pk)
                qs.update(is_default=False)
            super().save(*args, **kwargs)

    def format_zip_code(self):
        return re.sub(r"(\d{5})(\d{3})", r"\1-\2", self.zip_code)

    def __str__(self):
        if not self.street:
            return f"{self.format_zip_code()}"
        return f"{self.street}{f', {self.number}' if self.number else ''} - {self.neighborhood}, {self.city} - {self.state}, {self.zip_code}"
