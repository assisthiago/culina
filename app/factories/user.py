import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):

    username = factory.Faker("user_name")
    first_name = factory.Faker("first_name", locale="pt_BR")
    last_name = factory.Faker("last_name", locale="pt_BR")
    email = factory.LazyAttribute(lambda obj: f"{obj.first_name.lower()}.{obj.last_name.lower()}@email.com")
    password = factory.PostGenerationMethodCall("set_password", "defaultpassword")
    is_staff = factory.Faker("boolean")

    class Meta:
        model = User
