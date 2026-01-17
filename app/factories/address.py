import factory

from app.account.models import Address
from app.factories.account import AccountFactory
from app.factories.base import BaseFactory
from app.factories.store import StoreFactory


class AddressFactory(BaseFactory):

    account = factory.SubFactory(AccountFactory)
    store = factory.SubFactory(StoreFactory)
    label = factory.Faker("word", locale="pt_BR")
    is_default = factory.Faker("boolean")
    zip_code = factory.Faker("postcode", locale="pt_BR")
    street = factory.Faker("street_name", locale="pt_BR")
    number = factory.Faker("building_number", locale="pt_BR")
    neighborhood = factory.Faker("city_suffix", locale="pt_BR")
    complement = factory.Faker("secondary_address", locale="pt_BR")
    reference = factory.Faker("sentence", locale="pt_BR")
    city = factory.Faker("city", locale="pt_BR")
    state = factory.Faker("state_abbr", locale="pt_BR")
    latitude = factory.Faker("latitude", locale="pt_BR")
    longitude = factory.Faker("longitude", locale="pt_BR")

    class Meta:
        model = Address
