from django.urls import reverse
from django.utils.safestring import mark_safe
from unfold.admin import display

from app.utils import BaseTableSection


class ProductsSection(BaseTableSection):
    verbose_name = "Produtos"
    height = 300
    related_name = "products"
    fields = ("see_more", "name", "price", "discount_percentage", "is_active")
    ordering = ("position",)

    @display(description="")
    def see_more(self, obj):
        href = reverse("admin:product_product_change", args=[obj.id])
        return mark_safe(f'<a href="{href}" class="material-symbols-outlined">visibility</a>')


class SectionsSection(BaseTableSection):
    verbose_name = "Seções"
    height = 300
    related_name = "sections"
    fields = (
        "see_more",
        "title",
    )
    ordering = ("position",)

    @display(description="")
    def see_more(self, obj):
        href = reverse("admin:product_section_change", args=[obj.id])
        return mark_safe(f'<a href="{href}" class="material-symbols-outlined">visibility</a>')
