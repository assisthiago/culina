from django.conf import settings
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.decorators import display
from unfold.sections import TableSection

from app.common.mixin import StoreSessionScopeAdminMixin


class BaseAdmin(StoreSessionScopeAdminMixin, ModelAdmin):
    """Base admin class with common configurations."""

    list_per_page = settings.LIST_PER_PAGE

    list_filter = (
        ("created_at", RangeDateFilter),
        ("updated_at", RangeDateFilter),
    )

    list_display = (
        "see_more",
        "id",
        "uuid",
    )

    readonly_fields = (
        "uuid",
        "created_at",
        "updated_at",
    )

    @display(description="")
    def see_more(self, obj):
        return mark_safe('<span class="material-symbols-outlined">visibility</span>')


class BaseTableSection(TableSection):
    """Base table section with common configurations."""

    height = 300
    fields = ("see_more",)

    @display(description="")
    def see_more(self, obj):
        href = self.get_change_url(obj)
        return mark_safe(f'<a href="{href}" class="material-symbols-outlined">visibility</a>')
