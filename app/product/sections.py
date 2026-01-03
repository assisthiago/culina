from unfold.sections import TableSection


class ProductsSection(TableSection):
    verbose_name = "Produtos"
    height = 300
    related_name = "products"
    fields = ("name", "price", "discount_percentage", "is_active")
    ordering = ("position",)
