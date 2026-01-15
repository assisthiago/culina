from django.contrib import admin
from django.utils.translation import ngettext
from unfold.decorators import action, display

from app.order.inlines import OrderItemInline
from app.order.models import Order
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
                "account__user",
                "store",
            )
            .prefetch_related("items")
        )

    def get_actions(self, request):
        """Remove delete selected action."""
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        if request.GET.get("status") == Order.STATUS_PENDING:
            del actions["deliver_orders"]
        if request.GET.get("status") == Order.STATUS_PROCESSING:
            del actions["accept_orders"]
        if request.GET.get("status") == Order.STATUS_CANCELED:
            actions.clear()
        return actions

    # Changelist
    list_display = BaseAdmin.list_display + (
        "store",
        "account",
        "get_delivery_address",
        "get_total",
        "get_delivery_period",
        "get_duration",
    )
    list_filter = BaseAdmin.list_filter
    search_fields = (
        "uuid",
        "account__user__first_name",
        "account__user__last_name",
        "account__user__email",
    )
    search_help_text = "Buscar por UUID, nome ou email do cliente"
    list_sections = [OrderItemsSection]
    actions = ["accept_orders", "deliver_orders", "cancel_orders"]

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
    @display(description="Endereço de entrega")
    def get_delivery_address(self, obj):
        return obj.delivery_address()

    @display(description="Total")
    def get_total(self, obj):
        return obj.format_total()

    @display(description="Período para entrega", header=True)
    def get_delivery_period(self, obj):
        return obj.format_created_at(), obj.expected_delivery_time()

    @display(
        description="Duração",
        label={
            "success": "success",
            "warning": "warning",
            "danger": "danger",
        },
    )
    def get_duration(self, obj):
        status = "success"
        if percentage := obj.current_duration_percentage():
            status = "warning" if 60 <= percentage <= 80 else "danger"
        return status, obj.current_duration()

    # Actions
    def update_orders_status(self, request, queryset, status, message):
        """Update status for selected orders and display a message."""
        updated = queryset.update(status=status)
        self.message_user(
            request,
            ngettext(
                "%d pedido atualizado com sucesso. %s",
                "%d pedidos atualizados com sucesso. %s",
                updated,
            )
            % (updated, message),
        )

    @action(description="Aceitar pedidos selecionados")
    def accept_orders(self, request, queryset):
        self.update_orders_status(
            request,
            queryset,
            Order.STATUS_PROCESSING,
            "Os pedidos estão sendo processados.",
        )

    @action(description="Entregar pedidos selecionados")
    def deliver_orders(self, request, queryset):
        self.update_orders_status(
            request,
            queryset,
            Order.STATUS_DELIVERING,
            "Os pedidos saíram para entrega.",
        )

    @action(description="Cancelar pedidos selecionados")
    def cancel_orders(self, request, queryset):
        self.update_orders_status(
            request,
            queryset,
            Order.STATUS_CANCELED,
            "Os pedidos foram cancelados.",
        )
