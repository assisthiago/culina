import re
import unicodedata

import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory


def _ascii_slug(text: str) -> str:
    """
    Normaliza para ASCII e gera um slug simples com '.' como separador.
    Ex.: "João da Silva" -> "joao.da.silva"
    """
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", ".", text).strip(".")
    return text.lower()


class UserFactory(DjangoModelFactory):
    first_name = factory.Faker("first_name", locale="pt_BR")
    last_name = factory.Faker("last_name", locale="pt_BR")

    # Garantia de unicidade via Sequence, mantendo coerência com o nome da própria instância
    username = factory.Sequence(lambda n: f"usuario.{n}")

    email = factory.Sequence(lambda n: f"usuario.{n}@email.com")

    password = factory.PostGenerationMethodCall("set_password", "defaultpassword")
    is_staff = False

    class Meta:
        model = User

    @factory.post_generation
    def sync_username_email(self, create, extracted, **kwargs):
        """
        Após criar o usuário, ajusta username e email para refletirem first_name/last_name.
        Mantém unicidade adicionando o próprio id (create) ou um sufixo derivado do username (build).
        """
        base = _ascii_slug(f"{self.first_name}.{self.last_name}")

        if create and getattr(self, "id", None):
            suffix = self.id
        else:
            # build/sem id: usa o final numérico de username (usuario.<n>)
            try:
                suffix = int(str(self.username).split(".")[-1])
            except Exception:
                suffix = 0

        self.username = f"{base}.{suffix}"
        self.email = f"{base}.{suffix}@email.com"

        if create:
            self.save(update_fields=["username", "email"])
