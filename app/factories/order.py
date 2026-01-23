from decimal import Decimal

import factory

from app.account.models import Account
from app.factories.account import AccountFactory
from app.factories.base import BaseFactory
from app.factories.store import StoreFactory
from app.order.models import Order


class OrderFactory(BaseFactory):
    store = factory.SubFactory(StoreFactory)
    account = factory.SubFactory(AccountFactory, type=Account.TYPE_CLIENT)

    status = factory.Iterator(
        [
            Order.STATUS_PENDING,
            Order.STATUS_PROCESSING,
            Order.STATUS_DELIVERING,
            Order.STATUS_COMPLETED,
            Order.STATUS_CANCELED,
        ]
    )
    notes = factory.Faker("sentence", nb_words=12, locale="pt_BR")

    # Taxa de entrega pode ser 0.00 => NÃO usar positive=True
    delivery_fee = factory.Faker(
        "pydecimal",
        left_digits=2,
        right_digits=2,
        min_value=0,
        max_value=15,
    )

    # Subtotal > 0
    subtotal = factory.Faker(
        "pydecimal",
        left_digits=3,
        right_digits=2,
        positive=True,
        min_value=10,
        max_value=250,
    )

    total = factory.LazyAttribute(lambda o: (o.subtotal or Decimal("0.00")) + (o.delivery_fee or Decimal("0.00")))

    # Snapshot de endereço (o seu comando costuma sobrescrever tudo isso)
    zip_code = factory.Sequence(lambda n: f"{(10000000 + n) % 99999999:08d}")
    street = factory.Faker("street_name", locale="pt_BR")
    number = factory.Faker("building_number", locale="pt_BR")
    neighborhood = factory.Faker("bairro", locale="pt_BR")
    complement = factory.Iterator([None, "Apto 101", "Casa 2", "Fundos"])
    reference = factory.Iterator([None, "Próximo ao mercado", "Em frente à praça"])
    city = factory.Faker("city", locale="pt_BR")
    state = factory.Iterator(
        [
            "SP",
            "RJ",
            "MG",
            "PR",
            "SC",
            "RS",
            "BA",
            "PE",
            "CE",
            "DF",
        ]
    )
    latitude = factory.Faker("pydecimal", left_digits=2, right_digits=6, min_value=-33, max_value=5)
    longitude = factory.Faker("pydecimal", left_digits=2, right_digits=6, min_value=-74, max_value=-34)

    class Meta:
        model = Order
