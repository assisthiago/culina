from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from app.store.models import Store
from app.utils import BaseAdmin


@admin.register(Store)
class StoreAdmin(BaseAdmin):

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "account",
                "account__user",
            )
        )
