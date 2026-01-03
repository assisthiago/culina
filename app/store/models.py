from django.db import models

from app.account.models import Account
from app.utils import SoftDeleteModel, TimestampedModel


class Store(TimestampedModel, SoftDeleteModel):

    # Relations
    owner = models.OneToOneField(
        Account,
        verbose_name="dono",
        related_name="store",
        on_delete=models.CASCADE,
    )

    # Fields
    uuid = models.CharField(verbose_name="UUID", unique=True, max_length=36)
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
        help_text="Imagem retangular de 1296x200 pixels.",
    )
    config = models.JSONField(
        verbose_name="configuração",
        default=dict,
        blank=True,
        null=True,
        help_text="Configurações da loja em formato JSON.",
    )

    class Meta:
        verbose_name = "loja"
        verbose_name_plural = "lojas"
        db_table = "store"

    def __str__(self):
        return self.name
