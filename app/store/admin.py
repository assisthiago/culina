from django.contrib import admin

from app.store.inlines import OpeningHoursInline
from app.store.models import Store
from app.utils import BaseAdmin


@admin.register(Store)
class StoreAdmin(BaseAdmin):

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "owner",
                "owner__user",
            )
            .prefetch_related("opening_hours")
        )

    # Changelist
    list_display = (
        "see_more",
        "id",
        "name",
        "owner",
        "cnpj",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)

    # Changeform
    inlines = [OpeningHoursInline]
    fieldsets = (
        (
            "Informações",
            {
                "classes": ("tab",),
                "fields": (
                    "owner",
                    "name",
                    "cnpj",
                    "min_order_value",
                    "delivery_fee",
                ),
            },
        ),
        (
            "Imagens",
            {
                "classes": ("tab",),
                "fields": (
                    "thumbnail",
                    "banner",
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
    autocomplete_fields = ("owner",)
    readonly_fields = BaseAdmin.readonly_fields + (
        # "owner",
        # "cnpj",
        # "name",
    )
    # Display functions
    # Actions
