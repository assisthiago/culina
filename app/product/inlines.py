from unfold.admin import TabularInline

from app.product.models import Product


class ProductInline(TabularInline):

    model = Product
    tab = True
    extra = 0
    fields = ("name", "price", "is_active")
    readonly_fields = ("price",)
    ordering_field = "position"
    hide_ordering_field = True


class ProductSectionsInline(TabularInline):

    model = Product.sections.through
    tab = True
    extra = 0
    fields = ("section", "position")
    autocomplete_fields = ("section",)
    ordering_field = "position"
    hide_ordering_field = True
