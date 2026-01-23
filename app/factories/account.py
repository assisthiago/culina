import factory

from app.account.models import Account
from app.factories.base import BaseFactory
from app.factories.user import UserFactory


def _digits(n: int) -> str:
    return "".join(factory.Faker("random_digit").generate({}) for _ in range(n))


class AccountFactory(BaseFactory):
    type = factory.Iterator([Account.TYPE_CLIENT, Account.TYPE_ADMIN])

    user = factory.SubFactory(UserFactory)

    # 11 dígitos, sem pontuação
    cpf = factory.Sequence(lambda n: f"{n:011d}"[-11:])

    # 13 dígitos: 55 + DDD(2) + 9 + número(8)
    phone = factory.Sequence(lambda n: f"55{(11 + (n % 89)):02d}9{(10000000 + (n % 90000000)):08d}")

    class Meta:
        model = Account

    @factory.post_generation
    def sync_user_staff(self, create, extracted, **kwargs):
        """
        Mantém coerência: admin => user.is_staff=True, client => False.
        O model já faz isso no save(), mas aqui garantimos mesmo no build/test.
        """
        if not self.user:
            return
        should_be_staff = self.type == Account.TYPE_ADMIN
        self.user.is_staff = should_be_staff
        if create:
            self.user.save(update_fields=["is_staff"])
