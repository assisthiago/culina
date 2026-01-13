from django.urls import reverse
from django.utils.safestring import mark_safe
from unfold.admin import display

from app.utils import BaseTableSection


class OrderItemsSection(BaseTableSection):
    verbose_name = "Itens do pedido"
    height = 300
    related_name = "items"
    fields = ("see_more", "product_uuid", "product_name", "unit_price", "quantity")
    ordering = ("position",)

    @display(description="")
    def see_more(self, obj):
        href = reverse("admin:order_order_change", args=[obj.id])
        return mark_safe(f'<a href="{href}" class="material-symbols-outlined">visibility</a>')
