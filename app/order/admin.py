from django.contrib import admin
from unfold.decorators import display

from app.order.inlines import OrderItemInline
from app.order.models import Order, OrderItem
from app.order.sections import OrderItemsSection
from app.utils import BaseAdmin


@admin.register(Order)
class OrderAdmin(BaseAdmin):

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "account",
            )
            .prefetch_related("items")
        )

    # Changelist
    list_display = BaseAdmin.list_display + (
        "store",
        "account",
        "status",
        "total",
    )
    list_filter = BaseAdmin.list_filter
    search_fields = ("id", "uuid")
    search_help_text = "Buscar por ID ou UUID"
    sections = [OrderItemsSection]

    # Changeform
    fieldsets = (
        (
            "Informações",
            {
                "classes": ("tab",),
                "fields": (
                    "store",
                    "account",
                    "status",
                    "delivery_fee",
                    "subtotal",
                    "total",
                    "notes",
                ),
            },
        ),
        (
            "Endereço de entrega",
            {
                "classes": ("tab",),
                "fields": (
                    "zip_code",
                    "street",
                    "number",
                    "neighborhood",
                    "complement",
                    "reference",
                    "city",
                    "state",
                ),
            },
        ),
        (
            "Geolocalização",
            {
                "classes": ("tab",),
                "fields": (
                    "latitude",
                    "longitude",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "classes": ("tab",),
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )
    inlines = [OrderItemInline]
    autocomplete_fields = ("store", "account")
    readonly_fields = BaseAdmin.readonly_fields + ("latitude", "longitude")

    # Display methods
    @display(
        description="Status",
        label={
            Order.STATUS_PENDING: "warning",
            Order.STATUS_PROCESSING: "info",
            Order.STATUS_DELIVERING: "primary",
            Order.STATUS_COMPLETED: "success",
            Order.STATUS_CANCELED: "danger",
        },
    )
    def get_status(self, obj):
        return obj.get_status_display()

    # Actions


@admin.register(OrderItem)
class OrderItemAdmin(BaseAdmin):

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "order",
            )
        )

    # Changelist

    # Changeform
    fieldsets = (
        (
            "Informações",
            {
                "classes": ("tab",),
                "fields": (
                    "order",
                    "product_uuid",
                    "product_name",
                    "unit_price",
                    "quantity",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "classes": ("tab",),
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )
    autocomplete_fields = ("order",)
    # Display methods
    # Actions
