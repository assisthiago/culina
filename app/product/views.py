from django.db.models import Prefetch

from app.product.models import Product, Section
from app.product.serializers import ProductSerializer, SectionSerializer
from app.utils import BaseModelViewSet


class SectionViewSet(BaseModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


class ProductViewSet(BaseModelViewSet):
    queryset = (
        Product.objects.select_related(
            "store",
            "section",
        )
        .prefetch_related(
            "sections",
            Prefetch(
                "section__products",
                queryset=Product.objects.order_by("position"),
                to_attr="prefetched_products",
            ),
            Prefetch(
                "sections__products",
                queryset=Product.objects.order_by("position"),
                to_attr="prefetched_products",
            ),
        )
        .order_by("position")
    )
    serializer_class = ProductSerializer
