import factory

from app.account.models import Account
from app.factories.account import AccountFactory
from app.factories.base import BaseFactory
from app.store.models import Store


class StoreFactory(BaseFactory):

    owner = factory.SubFactory(AccountFactory, type=Account.TYPE_ADMIN)
    name = factory.Faker("company", locale="pt_BR")
    fantasy_name = factory.LazyAttribute(lambda obj: f"{obj.name} Fantasia")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))
    cnpj = factory.Faker("cnpj", locale="pt_BR")
    thumbnail = factory.Faker("image_url", width=200, height=200)
    banner = factory.Faker("image_url", width=800, height=200)
    min_order_value = factory.Faker(
        "pydecimal",
        left_digits=3,
        right_digits=2,
        positive=True,
        min_value=10,
        max_value=100,
    )
    delivery_time = factory.Faker("random_int", min=20, max=120)
    delivery_fee = factory.Faker(
        "pydecimal",
        left_digits=2,
        right_digits=2,
        positive=True,
        min_value=0,
        max_value=20,
    )

    class Meta:
        model = Store
