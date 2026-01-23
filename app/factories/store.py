import factory
from factory.django import ImageField

from app.account.models import Account
from app.factories.account import AccountFactory
from app.factories.base import BaseFactory
from app.store.models import Store

STORE_FANTASY_NAMES = [
    "Pizzaria do Zé",
    "Hamburgueria São Jorge",
    "Cantina da Vila",
    "Padaria Pão Quente",
    "Restaurante Sabor Caseiro",
    "Açaí do Norte",
    "Sushi House Brasil",
    "Espetinho do Bairro",
    "Doces & Delícias",
    "Lanchonete Central",
]


class StoreFactory(BaseFactory):
    owner = factory.SubFactory(AccountFactory, type=Account.TYPE_ADMIN)

    fantasy_name = factory.Iterator(STORE_FANTASY_NAMES)
    name = factory.LazyAttribute(lambda o: f"{o.fantasy_name} LTDA")

    cnpj = factory.Sequence(lambda n: f"{(10000000000000 + n) % 99999999999999:014d}")

    thumbnail = ImageField(width=75, height=75)
    banner = ImageField(width=1920, height=1080)

    min_order_value = factory.Faker(
        "pydecimal",
        left_digits=2,
        right_digits=2,
        positive=True,
        min_value=10,
        max_value=80,
    )

    delivery_time = factory.Faker("random_int", min=25, max=90)

    # max_value=15 precisa caber em left_digits => left_digits=2
    delivery_fee = factory.Faker(
        "pydecimal",
        left_digits=2,
        right_digits=2,
        min_value=0,
        max_value=15,
    )

    class Meta:
        model = Store
