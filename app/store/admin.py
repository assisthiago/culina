from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.views import View

from app.account.inlines import AddressInline
from app.common.admin import BaseAdmin
from app.store.inlines import OpeningHoursInline
from app.store.models import Store
from app.store.sections import OpeningHoursSection

SESSION_ACTIVE_STORE_ID = "admin_active_store_id"


class StoreSetActiveView(View):
    """
    View to set the active store in the admin session.
    1. If no store_id is provided, it clears the active store.
    2. If a valid store_id is provided, it sets that store as active for the user's session.
    3. Redirects back to the referring page with a success or error message.
    """

    def get(self, request: HttpRequest, *args, **kwargs):
        store_id = request.GET.get("store_id") or ""

        if not store_id:
            request.session.pop(SESSION_ACTIVE_STORE_ID, None)
            messages.success(request, "Exibindo todas as lojas.")
            return self._redirect_back(request)

        account = getattr(request.user, "account", None)
        if not account:
            messages.error(request, "Conta inválida.")
            return self._redirect_back(request)

        store = Store.objects.filter(id=store_id, owner=account).first()
        if not store:
            messages.error(request, "Loja inválida.")
            return self._redirect_back(request)

        request.session[SESSION_ACTIVE_STORE_ID] = int(store_id)
        messages.success(request, f"{store.fantasy_name} selecionada.")
        return self._redirect_back(request)

    def _redirect_back(self, request: HttpRequest) -> HttpResponseRedirect:
        to = request.META.get("HTTP_REFERER") or reverse("admin:index")
        return HttpResponseRedirect(to)


@admin.register(Store)
class StoreAdmin(BaseAdmin):

    scope_field = "pk"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "owner",
                "owner__user",
            )
            .prefetch_related("opening_hours")
        )

    # Changelist
    list_display = BaseAdmin.list_display + (
        "name",
        "owner",
        "cnpj",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)
    list_sections = [OpeningHoursSection]

    # Changeform
    inlines = [OpeningHoursInline, AddressInline]
    fieldsets = (
        (
            "Informações",
            {
                "classes": ("tab",),
                "fields": (
                    "owner",
                    "name",
                    "cnpj",
                    "min_order_value",
                    "delivery_fee",
                ),
            },
        ),
        (
            "Imagens",
            {
                "classes": ("tab",),
                "fields": (
                    "thumbnail",
                    "banner",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "classes": ("tab",),
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )
    autocomplete_fields = ("owner",)
    readonly_fields = BaseAdmin.readonly_fields + (
        "owner",
        "cnpj",
        "name",
    )
    # Display functions
    # Actions
