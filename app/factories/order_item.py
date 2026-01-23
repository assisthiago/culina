import uuid

import factory

from app.factories.base import BaseFactory
from app.factories.order import OrderFactory
from app.order.models import OrderItem

ORDER_ITEM_NAMES = [
    "Pizza Margherita",
    "X-Bacon",
    "Batata Frita",
    "Coca-Cola 350ml",
    "Açaí 500ml",
    "Pudim",
    "Pastel de Carne",
    "Coxinha",
]


class OrderItemFactory(BaseFactory):
    order = factory.SubFactory(OrderFactory)

    product_uuid = factory.LazyFunction(uuid.uuid4)
    product_name = factory.Iterator(ORDER_ITEM_NAMES)

    unit_price = factory.Faker(
        "pydecimal",
        left_digits=2,
        right_digits=2,
        positive=True,
        min_value=5,
        max_value=120,
    )
    quantity = factory.Faker("random_int", min=1, max=5)

    class Meta:
        model = OrderItem
