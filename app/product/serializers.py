from app.product.models import Product, Section
from app.utils import BaseSerializer


# Lite serializers for nested representation
class ProductInnerSerializer(BaseSerializer):

    class Meta:
        model = Product
        exclude = BaseSerializer.Meta.exclude + (
            "section",
            "sections",
            "store",
        )
        ordering = ["position"]


class SectionLiteSerializer(BaseSerializer):

    # Nested representations
    products = ProductInnerSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        exclude = BaseSerializer.Meta.exclude + ("store",)
        ordering = ["position"]


class ProductLiteSerializer(BaseSerializer):

    class Meta:
        model = Product
        exclude = BaseSerializer.Meta.exclude + ("store",)
        ordering = ["position"]


# Full serializers
class ProductSerializer(BaseSerializer):

    # Nested representations
    section = SectionLiteSerializer(many=False, read_only=True)
    sections = SectionLiteSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        exclude = BaseSerializer.Meta.exclude + ("store",)
        ordering = ["position"]


class SectionSerializer(BaseSerializer):

    # Nested representations
    products = ProductLiteSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        exclude = BaseSerializer.Meta.exclude + ("store",)
