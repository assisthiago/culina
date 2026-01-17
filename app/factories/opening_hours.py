import factory

from app.factories.base import BaseFactory
from app.factories.store import StoreFactory
from app.store.models import OpeningHours


class OpeningHoursFactory(BaseFactory):

    store = factory.SubFactory(StoreFactory)
    weekday = factory.Iterator([1, 2, 3, 4, 5, 6, 7])
    from_hour = factory.Faker("time", pattern="%H:%M:%S")
    to_hour = factory.LazyAttribute(
        lambda obj: (
            (factory.Faker("time", pattern="%H:%M:%S").generate({})) if obj.from_hour < "23:00:00" else "23:59:59"
        )
    )

    class Meta:
        model = OpeningHours
