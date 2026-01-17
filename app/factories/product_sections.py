import factory
from factory.django import DjangoModelFactory

from app.factories.product import ProductFactory
from app.factories.section import SectionFactory
from app.product.models import ProductSections


class ProductSectionFactory(DjangoModelFactory):
    """Factory for creating ProductSection instances for testing."""

    product = factory.SubFactory(ProductFactory)
    section = factory.SubFactory(SectionFactory)
    position = factory.Sequence(lambda n: n)

    class Meta:
        model = ProductSections
