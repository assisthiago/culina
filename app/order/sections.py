from django.urls import reverse
from django.utils.safestring import mark_safe
from unfold.admin import display

from app.utils import BaseTableSection


class OrderItemsSection(BaseTableSection):
    verbose_name = "Itens do pedido"
    height = 300
    related_name = "items"
    fields = ("product_name", "unit_price", "quantity")
