from django.urls import reverse
from django.utils.safestring import mark_safe
from unfold.admin import display

from app.common.admin import BaseTableSection


class OpeningHoursSection(BaseTableSection):
    verbose_name = "Horários de funcionamento"
    height = 300
    related_name = "opening_hours"
    fields = (
        "weekday",
        "from_hour",
        "to_hour",
    )
    ordering = ("weekday",)
