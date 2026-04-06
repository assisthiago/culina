from app.common.models import BaseModelViewSet
from app.store.models import Store
from app.store.serializers import StoreSerializer


class StoreViewSet(BaseModelViewSet):

    queryset = Store.objects.select_related(
        "owner",
        "owner__user",
    ).prefetch_related(
        "opening_hours",
        "addresses",
    )

    serializer_class = StoreSerializer
