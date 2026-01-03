from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from app.documentation import schema_view

router = routers.DefaultRouter()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls), name="api"),
]

if settings.DEBUG:
    urlpatterns += [
        path("health/", include("health_check.urls")),
        path("api/auth/", include("rest_framework.urls"), name="api_auth"),
        path("api/swagger.<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
        path("api/swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
        path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    ] + debug_toolbar_urls()
