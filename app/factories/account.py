import factory

from app.account.models import Account
from app.factories.base import BaseFactory
from app.factories.user import UserFactory


class AccountFactory(BaseFactory):

    user = factory.SubFactory(
        UserFactory,
        is_staff=factory.LazyAttribute(
            lambda obj: obj.type == Account.TYPE_ADMIN,
        ),
    )
    type = factory.Iterator([Account.TYPE_CLIENT, Account.TYPE_ADMIN])
    cpf = factory.Faker("cpf", locale="pt_BR")
    phone = factory.Faker("phone_number", locale="pt_BR")

    class Meta:
        model = Account
