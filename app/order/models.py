from decimal import Decimal

from django.db import models
from django.db.models import F, Sum
from django.db.models.functions import Coalesce

from app.account.models import Account
from app.store.models import Store
from app.utils import BaseModel


class Order(BaseModel):

    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_DELIVERING = "delivering"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendente"),
        (STATUS_PROCESSING, "Processando"),
        (STATUS_DELIVERING, "Entregando"),
        (STATUS_COMPLETED, "Concluído"),
        (STATUS_CANCELED, "Cancelado"),
    ]

    # Relationships
    store = models.ForeignKey(
        Store,
        verbose_name="loja",
        on_delete=models.PROTECT,
        related_name="orders",
    )
    account = models.ForeignKey(
        Account,
        verbose_name="cliente",
        on_delete=models.PROTECT,
        related_name="orders",
    )

    # Fields
    status = models.CharField(
        "status",
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    notes = models.TextField(
        verbose_name="observações",
        null=True,
        blank=True,
    )
    delivery_fee = models.DecimalField(
        verbose_name="taxa de entrega",
        max_digits=10,
        decimal_places=2,
        default=0.0,
    )
    subtotal = models.DecimalField(
        verbose_name="subtotal",
        max_digits=10,
        decimal_places=2,
        default=0.0,
    )
    total = models.DecimalField(
        verbose_name="total",
        max_digits=10,
        decimal_places=2,
        default=0.0,
    )

    # Address fields snapshot
    zip_code = models.CharField(
        verbose_name="CEP",
        db_index=True,
        max_length=8,
    )
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
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"
        db_table = "order"
        ordering = ["-created_at"]

    def recalculate_totals(self):
        agg = self.items.aggregate(subtotal=Coalesce(Sum(F("unit_price") * F("quantity")), Decimal("0.00")))
        self.subtotal = agg["subtotal"] or Decimal("0.00")
        self.total = (self.subtotal or Decimal("0.00")) + (self.delivery_fee or Decimal("0.00"))

    def __str__(self):
        return str(self.uuid)


class OrderItem(BaseModel):

    # Relationships
    order = models.ForeignKey(
        Order,
        verbose_name="pedido",
        on_delete=models.CASCADE,
        related_name="items",
    )

    # Fields
    product_uuid = models.UUIDField(verbose_name="UUID do produto")
    product_name = models.CharField(verbose_name="nome do produto", max_length=255)
    unit_price = models.DecimalField(
        verbose_name="preço unitário",
        max_digits=10,
        decimal_places=2,
    )
    quantity = models.PositiveIntegerField(verbose_name="quantidade", default=1)

    class Meta:
        verbose_name = "item do pedido"
        verbose_name_plural = "itens do pedido"
        db_table = "order_item"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["order", "product_uuid"], name="unique_product_per_order"),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"
