import factory
from factory.django import DjangoModelFactory


class BaseFactory(DjangoModelFactory):
    """Base factory class for creating model instances in tests."""

    uuid = factory.Faker("uuid4")
    created_at = factory.Faker("date_time_this_decade")
    updated_at = factory.Faker("date_time_this_decade")

    class Meta:
        abstract = True
