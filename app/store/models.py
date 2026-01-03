from django.db import models
from django.db.models import F, Q

from app.account.models import Account
from app.utils import BaseModel


class OpeningHours(models.Model):

    WEEKDAYS = [
        (1, "Segunda-feira"),
        (2, "Terça-feira"),
        (3, "Quarta-feira"),
        (4, "Quinta-feira"),
        (5, "Sexta-feira"),
        (6, "Sábado"),
        (7, "Domingo"),
    ]

    # Relations
    store = models.ForeignKey(
        "Store",
        verbose_name="loja",
        related_name="opening_hours",
        on_delete=models.CASCADE,
    )

    # Fields
    weekday = models.PositiveSmallIntegerField(
        verbose_name="dia da semana",
        choices=WEEKDAYS,
    )
    from_hour = models.TimeField(verbose_name="abre às")
    to_hour = models.TimeField(verbose_name="fecha às")

    class Meta:
        verbose_name = "horário de funcionamento"
        verbose_name_plural = "horários de funcionamento"
        db_table = "opening_hours"
        ordering = ("weekday", "from_hour")
        constraints = [
            models.CheckConstraint(
                condition=Q(from_hour__lt=F("to_hour")),
                name="opening_hours_from_lt_to",
            ),
            models.UniqueConstraint(
                fields=["store", "weekday"],
                name="opening_hours_unique_interval",
            ),
        ]

    def __str__(self):
        return f"{self.get_weekday_display()} {self.from_hour}–{self.to_hour}"


class Store(BaseModel):

    # Relations
    owner = models.OneToOneField(
        Account,
        verbose_name="dono",
        related_name="store",
        on_delete=models.CASCADE,
    )

    # Fields

    name = models.CharField(verbose_name="nome", max_length=100)
    cnpj = models.CharField(verbose_name="CNPJ", unique=True, max_length=14)
    thumbnail = models.ImageField(
        verbose_name="miniatura",
        upload_to="stores/thumbnails/",
        help_text="Imagem quadrada de 75x75 pixels.",
    )
    banner = models.ImageField(
        verbose_name="banner",
        upload_to="stores/banners/",
        help_text="Imagem retangular de 1920x1080 pixels.",
    )
    min_order_value = models.DecimalField(
        verbose_name="valor mínimo do pedido",
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Valor mínimo do pedido. Em reais (R$).",
    )
    delivery_fee = models.DecimalField(
        verbose_name="taxa de entrega",
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Taxa fixa cobrada por entrega. Em reais (R$).",
    )

    class Meta:
        verbose_name = "loja"
        verbose_name_plural = "lojas"
        db_table = "store"

    def __str__(self):
        return self.name
