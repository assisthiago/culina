import factory
from factory.django import ImageField

from app.factories.base import BaseFactory
from app.factories.section import SectionFactory
from app.factories.store import StoreFactory
from app.product.models import Product

PRODUCT_NAMES = [
    "Pizza Margherita",
    "Pizza Calabresa",
    "Pizza Portuguesa",
    "X-Bacon",
    "X-Salada",
    "Hambúrguer Artesanal",
    "Batata Frita",
    "Coxinha",
    "Pastel de Carne",
    "Açaí 500ml",
    "Brigadeiro",
    "Pudim",
    "Coca-Cola 350ml",
    "Guaraná Antarctica 350ml",
    "Suco de Laranja 300ml",
    "Água Mineral 500ml",
    "Esfiha de Frango",
    "Kibe",
    "Sushi Combo 12 peças",
    "Temaki Salmão",
]


class ProductFactory(BaseFactory):
    store = factory.SubFactory(StoreFactory)
    section = factory.SubFactory(SectionFactory)

    name = factory.Iterator(PRODUCT_NAMES)
    description = factory.Faker("sentence", nb_words=12, locale="pt_BR")

    # Preço > 0
    price = factory.Faker(
        "pydecimal",
        left_digits=3,
        right_digits=2,
        positive=True,
        min_value=5,
        max_value=120,
    )

    # Desconto pode ser 0 => NÃO usar positive=True
    discount_percentage = factory.Faker(
        "pydecimal",
        left_digits=2,
        right_digits=2,
        min_value=0,
        max_value=25,
    )

    position = factory.Sequence(lambda n: n)
    is_active = True

    picture = ImageField(width=640, height=480)
    thumbnail = ImageField(width=85, height=85)

    class Meta:
        model = Product
