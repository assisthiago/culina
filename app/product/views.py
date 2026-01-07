from app.product.models import Product, Section
from app.product.serializers import ProductSerializer, SectionSerializer
from app.utils import BaseModelViewSet


class SectionViewSet(BaseModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


class ProductViewSet(BaseModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
