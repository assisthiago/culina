from rest_framework import serializers

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
    products = serializers.SerializerMethodField()

    class Meta:
        model = Section
        exclude = BaseSerializer.Meta.exclude + ("store",)
        ordering = ["position"]

    def get_products(self, obj):
        products = getattr(obj, "prefetched_products", None)
        if products is None:
            # Fallback if prefetched_products is not set
            products = obj.products.all()
        return ProductInnerSerializer(products, many=True, context=self.context).data


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
    products = serializers.SerializerMethodField()

    class Meta:
        model = Section
        exclude = BaseSerializer.Meta.exclude + ("store",)

    def get_products(self, obj):
        products = getattr(obj, "prefetched_products", None)
        if products is None:
            products = obj.products.all()
        return ProductLiteSerializer(products, many=True, context=self.context).data
