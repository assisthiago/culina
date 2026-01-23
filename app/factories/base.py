import factory
from factory.django import DjangoModelFactory


class BaseFactory(DjangoModelFactory):
    """
    Base factory para modelos com BaseModel (uuid, created_at, updated_at).
    """

    uuid = factory.Faker("uuid4")
    created_at = factory.Faker("date_time_this_decade", tzinfo=None)
    updated_at = factory.Faker("date_time_this_decade", tzinfo=None)

    class Meta:
        abstract = True
