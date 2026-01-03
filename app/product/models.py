# Create your models here.
from django.db import models

from app.store.models import Store
from app.utils import BaseModel


class Section(BaseModel):

    TYPE_SLIDER = "slider"
    TYPE_LIST = "list"
    TYPE_GRID = "grid"
    SECTION_TYPES = [
        (TYPE_GRID, "Grade"),
        (TYPE_LIST, "Lista"),
        (TYPE_SLIDER, "Slider"),
    ]

    FORM_NA = "not_applicable"
    FORM_RADIO = "radio"
    FORM_INCREMENT_DECREMENT = "increment_decrement"
    FORM_TEXTBOX = "textbox"
    FORM_CHOICES = [
        (FORM_NA, "N/A"),
        (FORM_RADIO, "Apenas um"),
        (FORM_INCREMENT_DECREMENT, "Incrementar/Decrementar"),
        (FORM_TEXTBOX, "Observação"),
    ]

    # Relations
    store = models.ForeignKey(
        Store,
        verbose_name="loja",
        related_name="sections",
        on_delete=models.CASCADE,
    )

    # Fields
    title = models.CharField(verbose_name="título", max_length=100)
    position = models.PositiveIntegerField(verbose_name="posição", default=0)
    min_products = models.PositiveIntegerField(
        verbose_name="mínimo de produtos",
        default=0,
    )
    max_products = models.PositiveIntegerField(
        verbose_name="máximo de produtos",
        default=0,
    )
    is_active = models.BooleanField(verbose_name="ativo", default=False)
    is_required = models.BooleanField(verbose_name="obrigatório", default=False)
    is_highlighted = models.BooleanField(verbose_name="destaque", default=False)
    form = models.CharField(
        verbose_name="formulário",
        max_length=50,
        choices=FORM_CHOICES,
        default=FORM_NA,
    )
    textbox_help_text = models.CharField(
        verbose_name="texto de ajuda",
        max_length=255,
        blank=True,
        null=True,
        help_text="Texto de ajuda exibido abaixo do campo de observação. Exemplo: tirar a cebola, maionese à parte etc.",
    )

    class Meta:
        verbose_name = "seção"
        verbose_name_plural = "seções"
        db_table = "section"
        ordering = ["position"]

    def __str__(self):
        return self.title


class Product(BaseModel):

    # Relations
    store = models.ForeignKey(
        Store,
        verbose_name="loja",
        related_name="products",
        on_delete=models.CASCADE,
    )
    section = models.ForeignKey(
        Section,
        verbose_name="seção",
        related_name="products",
        on_delete=models.CASCADE,
    )
    sections = models.ManyToManyField(
        Section,
        verbose_name="seções",
        related_name="products_many",
        blank=True,
        through="ProductSections",
    )

    # Fields
    name = models.CharField(verbose_name="nome", max_length=100)
    description = models.TextField(
        verbose_name="descrição",
        blank=True,
        null=True,
    )
    price = models.DecimalField(
        verbose_name="preço",
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )
    discount_percentage = models.DecimalField(
        verbose_name="porcentagem de desconto",
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Porcentagem de desconto aplicada ao preço do produto. Para um desconto de 10%, insira 10.00.",
    )
    position = models.PositiveIntegerField(
        verbose_name="posição",
        default=0,
        help_text="Define a ordem de exibição dos produtos na seção.",
    )
    is_active = models.BooleanField(verbose_name="ativo", default=False)
    picture = models.ImageField(
        verbose_name="imagem",
        upload_to="products/images/",
        help_text="Imagem principal do produto.",
    )
    thumbnail = models.ImageField(
        verbose_name="miniatura",
        upload_to="products/thumbnails/",
        help_text="Imagem quadrada de 85x85 pixels.",
    )

    class Meta:
        verbose_name = "produto"
        verbose_name_plural = "produtos"
        db_table = "product"
        ordering = ["position"]

    def __str__(self):
        return self.name


# Through model for ManyToMany relationship between Product and Section
class ProductSections(models.Model):

    # Relations
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="section_products",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_sections",
    )

    # Fields
    position = models.PositiveIntegerField(verbose_name="posição", default=0)

    class Meta:
        verbose_name = "Seção do Produto"
        verbose_name_plural = "Seções dos Produtos"
        db_table = "through_product_sections"
        ordering = ["position"]

    def __str__(self):
        return f"{self.product.name} do {self.section.title}"
