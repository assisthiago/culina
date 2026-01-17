import factory

from app.factories.base import BaseFactory
from app.factories.section import SectionFactory
from app.factories.store import StoreFactory
from app.product.models import Product


class ProductFactory(BaseFactory):

    store = factory.SubFactory(StoreFactory)
    section = factory.SubFactory(SectionFactory)
    sections = factory.RelatedFactoryList(
        SectionFactory,
        factory_related_name="products",
        size=factory.Faker("random_int", min=3, max=10),
    )
    name = factory.Faker("food")
    description = factory.Faker("paragraph", nb_sentences=3)
    price = factory.Faker(
        "pydecimal",
        left_digits=3,
        right_digits=2,
        positive=True,
    )
    discount_percentage = factory.Faker(
        "pydecimal",
        left_digits=2,
        right_digits=2,
        positive=True,
    )
    position = factory.Sequence(lambda n: n)
    is_active = factory.Faker("boolean", chance_of_getting_true=80)
    picture = factory.Faker("image_url", width=640, height=480)
    thumbnail = factory.Faker("image_url", width=100, height=100)

    class Meta:
        model = Product
