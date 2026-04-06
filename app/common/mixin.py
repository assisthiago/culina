from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from django.http import HttpRequest

from app.common.utils import get_active_store_id


class StoreSessionScopeAdminMixin:
    """
    Applies a global filter by active store (session) in the Django Admin.

    Usage:
      class OrderAdmin(StoreSessionScopeAdminMixin, BaseAdmin):
          scope_field = "store"           # Direct FK to Store
          # or "order__store" etc.
    """

    scope_field: Optional[str] = None  # ex: "store" | "order__store" | "product__store"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        active_store_id = get_active_store_id(request)
        if not active_store_id:
            return qs

        if not self.scope_field:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} needs scope_field " "(ex: 'store' or 'order__store')."
            )

        return qs.filter(**{f"{self.scope_field}__id": active_store_id})
