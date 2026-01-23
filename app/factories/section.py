import factory

from app.factories.base import BaseFactory
from app.factories.store import StoreFactory
from app.product.models import Section

SECTION_TITLES = [
    "Bebidas",
    "Lanches",
    "Pizzas",
    "Sobremesas",
    "Combos",
    "Acompanhamentos",
    "Massas",
    "Saladas",
    "Molhos e Extras",
    "Personalize seu pedido",
]


class SectionFactory(BaseFactory):
    store = factory.SubFactory(StoreFactory)

    title = factory.Iterator(SECTION_TITLES)
    position = factory.Sequence(lambda n: n)

    # Mantemos regras simples e válidas:
    # min <= max sempre
    min_products = 0
    max_products = factory.Faker("random_int", min=1, max=5)

    is_active = True
    is_required = factory.Faker("boolean", chance_of_getting_true=25)
    is_highlighted = factory.Faker("boolean", chance_of_getting_true=15)

    form = factory.LazyAttribute(
        lambda o: Section.FORM_TEXTBOX if o.title == "Personalize seu pedido" else Section.FORM_NA
    )
    textbox_help_text = factory.LazyAttribute(
        lambda o: (
            "Ex.: tirar a cebola, maionese à parte, ponto da carne etc." if o.form == Section.FORM_TEXTBOX else None
        )
    )

    class Meta:
        model = Section
