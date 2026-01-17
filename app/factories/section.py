import factory

from app.factories.base import BaseFactory
from app.factories.store import StoreFactory
from app.product.models import Section


class SectionFactory(BaseFactory):

    store = factory.SubFactory(StoreFactory)
    title = factory.Faker("sentence", nb_words=4)
    position = factory.Sequence(lambda n: n)
    min_products = factory.Sequence(lambda n: n % 5)
    max_products = factory.Sequence(lambda n: (n % 5) + 5)
    is_active = factory.Faker("boolean", chance_of_getting_true=75)
    is_required = factory.Faker("boolean", chance_of_getting_true=50)
    is_highlighted = factory.Faker("boolean", chance_of_getting_true=30)
    form = factory.Faker(
        "random_element",
        elements=[choice[0] for choice in Section.FORM_CHOICES],
    )
    textbox_help_text = factory.Faker("sentence", nb_words=6)

    class Meta:
        model = Section
