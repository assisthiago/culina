from app.common.admin import BaseTableSection


class OrderItemsSection(BaseTableSection):
    verbose_name = "Itens do pedido"
    height = 300
    related_name = "items"
    fields = ("product_name", "unit_price", "quantity")
