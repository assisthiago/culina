from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from django.http import HttpRequest
from django.urls import reverse

from app.order.models import Order


def admin_url(name: str, **query: Any) -> str:
    url = reverse(name)
    if query:
        url = f"{url}?{urlencode(query)}"
    return url


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
