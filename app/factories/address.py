import re

import factory

from app.account.models import Address
from app.factories.account import AccountFactory
from app.factories.base import BaseFactory
from app.factories.store import StoreFactory

UF_CHOICES = [
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
]

ADDRESS_LABELS = ["Casa", "Trabalho", "Matriz", "Filial"]

COMPLEMENTS = [
    "Apto 101",
    "Apto 202",
    "Bloco B",
    "Fundos",
    "Casa 2",
    "Sala 301",
    "Cobertura",
    None,
    None,
    None,
]

REFERENCES = [
    "Próximo ao mercado",
    "Ao lado da farmácia",
    "Em frente à praça",
    "Perto do metrô",
    "Próximo ao hospital",
    None,
    None,
]


class AddressFactory(BaseFactory):
    """
    Regras do seu model:
    - XOR: address pertence OU a Account OU a Store (o comando garante isso ao sobrescrever).
    - zip_code: 8 dígitos (^\d{8}$)
    - state: 2 letras maiúsculas (UF)
    """

    # Defaults (o comando sobrescreve para cumprir XOR)
    account = factory.SubFactory(AccountFactory)
    store = None

    label = factory.Iterator(ADDRESS_LABELS)
    is_default = False

    # CEP: sempre 8 dígitos, sem hífen (compatível com constraint)
    zip_code = factory.Sequence(lambda n: f"{(10000000 + n) % 99999999:08d}")

    street = factory.Faker("street_name", locale="pt_BR")
    number = factory.Faker("building_number", locale="pt_BR")
    neighborhood = factory.Faker("bairro", locale="pt_BR")

    complement = factory.Iterator(COMPLEMENTS)
    reference = factory.Iterator(REFERENCES)

    city = factory.Faker("city", locale="pt_BR")
    state = factory.Iterator(UF_CHOICES)

    # Coordenadas plausíveis no Brasil (aproximado)
    latitude = factory.Faker("pydecimal", left_digits=2, right_digits=6, min_value=-33, max_value=5)
    longitude = factory.Faker("pydecimal", left_digits=2, right_digits=6, min_value=-74, max_value=-34)

    class Meta:
        model = Address

    @factory.post_generation
    def normalize_fields(self, create, extracted, **kwargs):
        # blindagem adicional: zip_code só dígitos e 8 chars
        z = re.sub(r"\D+", "", self.zip_code or "")
        self.zip_code = (z + "0" * 8)[:8]

        # UF garantida
        self.state = (self.state or "SP").upper()[:2]

        if create:
            self.save(update_fields=["zip_code", "state"])
