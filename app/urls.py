from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from app.account import views as account_views
from app.documentation import schema_view
from app.order import views as order_views
from app.product import views as product_views
from app.store import views as store_views

router = routers.DefaultRouter()
router.register(r"accounts", account_views.AccountViewSet, basename="account")
router.register(r"addresses", account_views.AddressViewSet, basename="address")
router.register(r"orders", order_views.OrderViewSet, basename="order")
router.register(r"products", product_views.ProductViewSet, basename="product")
router.register(r"sections", product_views.SectionViewSet, basename="section")
router.register(r"stores", store_views.StoreViewSet, basename="store")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls), name="api"),
]

if settings.DEBUG:
    urlpatterns += [
        path("health/", include("health_check.urls")),
        path("api/auth/", include("rest_framework.urls"), name="api_auth"),
        path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
        path("api/swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
        path("api/swagger.<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    ] + debug_toolbar_urls()

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
