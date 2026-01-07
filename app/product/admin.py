from django.contrib import admin

from app.product.inlines import ProductInline, ProductSectionsInline
from app.product.models import Product, Section
from app.product.sections import ProductsSection, SectionsSection
from app.utils import BaseAdmin


@admin.register(Section)
class SectionAdmin(BaseAdmin):

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "store",
            )
            .prefetch_related("products")
        )

    # Changelist
    search_fields = ("title",)
    list_display = (
        "see_more",
        "id",
        "title",
        "form",
        "is_active",
    )
    list_editable = ("is_active",)
    list_sections = [ProductsSection]

    # Changeform
    inlines = [ProductInline]
    fieldsets = (
        (
            "Informações",
            {
                "classes": ("tab",),
                "fields": (
                    "store",
                    "title",
                    "is_active",
                    "position",
                ),
            },
        ),
        (
            "Configurações",
            {
                "classes": ("tab",),
                "fields": (
                    "form",
                    "min_products",
                    "max_products",
                    "is_required",
                    "is_highlighted",
                    "textbox_help_text",
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
    autocomplete_fields = ("store",)
    readonly_fields = BaseAdmin.readonly_fields + ("position",)

    # Display functions
    # Actions


@admin.register(Product)
class ProductAdmin(BaseAdmin):

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "section",
                "section__store",
            )
            .prefetch_related("sections")
        )

    # Changelist
    search_fields = ("name",)
    list_display = (
        "see_more",
        "id",
        "name",
        "section",
        "price",
        "is_active",
    )
    list_editable = ("is_active",)
    list_sections = [SectionsSection]

    # Changeform
    inlines = [ProductSectionsInline]
    fieldsets = (
        (
            "Informações",
            {
                "classes": ("tab",),
                "fields": (
                    "store",
                    "section",
                    "name",
                    "description",
                    "is_active",
                    "position",
                ),
            },
        ),
        (
            "Valores",
            {
                "classes": ("tab",),
                "fields": (
                    "price",
                    "discount_percentage",
                ),
            },
        ),
        (
            "Imagens",
            {
                "classes": ("tab",),
                "fields": (
                    "picture",
                    "thumbnail",
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
    autocomplete_fields = (
        "store",
        "section",
    )
    readonly_fields = BaseAdmin.readonly_fields + ("position",)

    # Display functions
    # Actions
