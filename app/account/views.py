from app.account.models import Account, Address
from app.account.serializers import AccountSerializer, AddressSerializer
from app.utils import BaseModelViewSet


class AddressViewSet(BaseModelViewSet):
    queryset = Address.objects.select_related("account", "store")
    serializer_class = AddressSerializer


class AccountViewSet(BaseModelViewSet):
    queryset = Account.objects.prefetch_related("addresses")
    serializer_class = AccountSerializer
