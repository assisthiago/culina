import factory

from app.account.models import Account
from app.factories.account import AccountFactory
from app.factories.base import BaseFactory
from app.factories.store import StoreFactory
from app.order.models import Order


class OrderFactory(BaseFactory):

    store = factory.SubFactory(StoreFactory)
    account = factory.SubFactory(AccountFactory, type=Account.TYPE_CLIENT)
    status = factory.Faker(
        "random_element",
        elements=[choice[0] for choice in Order.STATUS_CHOICES],
    )
    notes = factory.Faker("paragraph", nb_sentences=3)
    delivery_fee = factory.Faker(
        "pydecimal",
        left_digits=3,
        right_digits=2,
        positive=True,
    )
    subtotal = factory.Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True,
    )
    total = factory.LazyAttribute(lambda o: o.subtotal + o.delivery_fee)
    zip_code = factory.Faker("postcode", locale="pt_BR")
    street = factory.Faker("street_name", locale="pt_BR")
    number = factory.Faker("building_number", locale="pt_BR")
    neighborhood = factory.Faker("city_suffix", locale="pt_BR")
    complement = factory.Faker("secondary_address", locale="pt_BR")
    reference = factory.Faker("landmark", locale="pt_BR")
    city = factory.Faker("city", locale="pt_BR")
    state = factory.Faker("state_abbr", locale="pt_BR")
    latitude = factory.Faker("latitude", locale="pt_BR")
    longitude = factory.Faker("longitude", locale="pt_BR")

    class Meta:
        model = Order
