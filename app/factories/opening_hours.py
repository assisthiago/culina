import datetime

import factory
from factory.django import DjangoModelFactory

from app.factories.store import StoreFactory
from app.store.models import OpeningHours


class OpeningHoursFactory(DjangoModelFactory):
    store = factory.SubFactory(StoreFactory)

    # normalmente o seed vai passar weekday explicitamente (1..7)
    weekday = factory.Iterator([1, 2, 3, 4, 5])

    # TimeField espera datetime.time
    from_hour = factory.Iterator([datetime.time(8, 0), datetime.time(9, 0), datetime.time(10, 0)])
    to_hour = factory.Iterator([datetime.time(18, 0), datetime.time(19, 0), datetime.time(20, 0)])

    class Meta:
        model = OpeningHours
