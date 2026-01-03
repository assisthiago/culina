from unfold.admin import TabularInline

from app.store.forms import OpeningHoursInlineForm
from app.store.models import OpeningHours


class OpeningHoursInline(TabularInline):
    model = OpeningHours
    form = OpeningHoursInlineForm
    tab = True
    extra = 0
    max_num = 7

    fields = ("weekday", "from_hour", "to_hour")
    ordering = ("weekday",)
