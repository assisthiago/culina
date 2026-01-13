from unfold.admin import TabularInline

from app.order.models import OrderItem


class OrderItemInline(TabularInline):

    model = OrderItem
    tab = True
    extra = 0
    fields = (
        "order",
        "product_uuid",
        "product_name",
        "unit_price",
        "quantity",
    )
    readonly_fields = ("order",)
