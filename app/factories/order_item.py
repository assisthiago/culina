import factory

from app.factories.base import BaseFactory
from app.factories.order import OrderFactory
from app.order.models import OrderItem


class OrderItemFactory(BaseFactory):

    order = factory.SubFactory(OrderFactory)
    product_uuid = factory.Faker("uuid4")
    product_name = factory.Faker("word")
    unit_price = factory.Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True,
    )
    quantity = factory.Faker(
        "random_int",
        min=1,
        max=10,
    )

    class Meta:
        model = OrderItem
