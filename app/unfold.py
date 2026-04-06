from typing import Any
from urllib.parse import urlencode

from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe

from app.order.models import Order
from app.store.models import Store

SESSION_ACTIVE_STORE_ID = "admin_active_store_id"


def admin_url(name: str, **query: Any) -> str:
    url = reverse(name)
    if query:
        url = f"{url}?{urlencode(query)}"
    return url


def dropdown_callback(request: HttpRequest) -> list[dict[str, Any]]:
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return []

    account = getattr(user, "account", None)
    if not account:
        return []

    stores = (
        Store.objects.filter(owner=account)
        .only(
            "id",
            "uuid",
            "fantasy_name",
        )
        .order_by("fantasy_name")
    )
    active_store = stores.filter(id=request.session.get(SESSION_ACTIVE_STORE_ID)).first()

    items: list[dict[str, Any]] = [
        {
            "icon": "storefront" if not active_store else "store",
            "title": "Todas as lojas",
            "link": admin_url("store_set_active", store_id=""),
            "active": lambda req: not req.session.get(SESSION_ACTIVE_STORE_ID),
        }
    ]

    for s in stores:
        items.append(
            {
                "icon": "storefront" if active_store and s.id == active_store.id else "store",
                "title": (
                    mark_safe(f"<b>{s.fantasy_name}</b>")
                    if active_store and s.id == active_store.id
                    else s.fantasy_name
                ),
                "link": admin_url("store_set_active", store_id=str(s.id)),
                "active": (lambda req, _id=s.id: req.session.get(SESSION_ACTIVE_STORE_ID) == _id),
            }
        )

    return items


def subheader_callback(request: HttpRequest) -> str:
    store_id = request.session.get(SESSION_ACTIVE_STORE_ID)
    if not store_id:
        return "Todas as lojas"
    store = Store.objects.filter(id=store_id).only("id", "fantasy_name").first()
    return store.fantasy_name


def tabs_callback(request: HttpRequest) -> list[dict[str, Any]]:
    return [
        {
            "models": ["order.order"],
            "items": [
                {
                    "title": "Pendentes",
                    "link": admin_url("admin:order_order_changelist", status=Order.STATUS_PENDING),
                    "active": lambda req: req.GET.get("status") == Order.STATUS_PENDING,
                },
                {
                    "title": "Em andamento",
                    "link": admin_url("admin:order_order_changelist", status=Order.STATUS_PROCESSING),
                    "active": lambda req: req.GET.get("status") == Order.STATUS_PROCESSING,
                },
                {
                    "title": "Saiu para entrega",
                    "link": admin_url("admin:order_order_changelist", status=Order.STATUS_DELIVERING),
                    "active": lambda req: req.GET.get("status") == Order.STATUS_DELIVERING,
                },
                {
                    "title": "Concluídos",
                    "link": admin_url("admin:order_order_changelist", status=Order.STATUS_COMPLETED),
                    "active": lambda req: req.GET.get("status") == Order.STATUS_COMPLETED,
                },
                {
                    "title": "Cancelados",
                    "link": admin_url("admin:order_order_changelist", status=Order.STATUS_CANCELED),
                    "active": lambda req: req.GET.get("status") == Order.STATUS_CANCELED,
                },
            ],
        },
    ]
