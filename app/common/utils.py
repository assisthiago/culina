import math
from typing import Optional

from django.conf import settings
from django.db import models
from django.db.models import QuerySet

from app.store.models import Store

SESSION_ACTIVE_STORE_ID = "admin_active_store_id"


def get_owner_stores_qs(request) -> QuerySet[Store]:
    account = getattr(request.user, "account", None)
    if not account:
        return Store.objects.none()
    return Store.objects.filter(owner=account).only("id", "uuid", "fantasy_name").order_by("fantasy_name")


def get_active_store_id(request) -> Optional[int]:
    return request.session.get(SESSION_ACTIVE_STORE_ID)


def set_active_store_id(request, store_id: Optional[int]) -> None:
    if store_id:
        request.session[SESSION_ACTIVE_STORE_ID] = int(store_id)
    else:
        request.session.pop(SESSION_ACTIVE_STORE_ID, None)


# Geographical functions
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on the Earth surface.

    Args:
        lat1 (float): Latitude of the first point in decimal degrees.
        lon1 (float): Longitude of the first point in decimal degrees.
        lat2 (float): Latitude of the second point in decimal degrees.
        lon2 (float): Longitude of the second point in decimal degrees.

    Returns:
        float: Distance between the two points in kilometers.
    """
    # Convert decimal degrees to radians
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return settings.EARTH_RADIUS_KM * c


def bounding_box(lat: float, lon: float, radius_km: float) -> tuple[float, float, float, float]:
    """Pre-filtering bounding box for a given point and radius.

    Args:
        lat (float): Latitude of the point in decimal degrees.
        lon (float): Longitude of the point in decimal degrees.
        radius_km (float): Radius in kilometers.

    Returns:
        tuple[float, float, float, float]: Bounding box as (min_lat, max_lat, min_lon, max_lon).
    """
    lat_delta = radius_km / 110.574  # 1st degree of latitude ~ 110.574 km
    cos_lat = math.cos(math.radians(lat))  # 1st degree of longitude ~ 111.320*cos(latitude) km
    lon_delta = radius_km / (111.320 * max(cos_lat, 1e-6))  # Avoid division by zero at poles
    return (lat - lat_delta, lat + lat_delta, lon - lon_delta, lon + lon_delta)


# Format functions
def format_phone(obj: models.Model) -> str:
    """Format phone number into standard representation.
    (999) 99999-9999 or (99) 9999-9999

    Args:
        obj (models.Model): Object with 'phone' attribute.

    Returns:
        str: Formatted phone number.
    """
    if len(obj.phone) == 11:
        return f"({obj.phone[:2]}) {obj.phone[2:7]}-{obj.phone[7:]}"
    elif len(obj.phone) == 10:
        return f"({obj.phone[:2]}) {obj.phone[2:6]}-{obj.phone[6:]}"
    return obj.phone
