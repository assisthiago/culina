import uuid as _uuid

from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny


class BaseModel(models.Model):

    uuid = models.UUIDField(
        verbose_name="UUID",
        unique=True,
        editable=False,
        default=_uuid.uuid4,
    )
    created_at = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="atualizado em", auto_now=True)

    class Meta:
        abstract = True


class LookupIdOrUuidMixin:
    """Mixin to allow lookup by either ID (pk) or UUID field."""

    uuid_field_name = "uuid"  # padrão do nome do campo

    def _is_uuid(self, value: str) -> bool:
        """Check if the given value is a valid UUID."""
        try:
            _uuid.UUID(str(value))
            return True
        except Exception:
            return False

    def _model_has_uuid_field(self) -> bool:
        """Check if the model has the specified UUID field."""
        model = self.get_queryset().model
        try:
            model._meta.get_field(self.uuid_field_name)
            return True
        except Exception:
            return False

    def get_object(self):
        """Retrieve the object based on either UUID or ID."""
        queryset = self.filter_queryset(self.get_queryset())

        lookup_kwarg = self.lookup_url_kwarg or self.lookup_field  # normalmente "pk"
        lookup_value = self.kwargs.get(lookup_kwarg)

        if lookup_value is None:
            raise AssertionError("Lookup value not found in URL kwargs.")

        if self._model_has_uuid_field() and self._is_uuid(lookup_value):
            obj = get_object_or_404(queryset, **{self.uuid_field_name: lookup_value})
        else:
            obj = get_object_or_404(queryset, pk=lookup_value)

        self.check_object_permissions(self.request, obj)
        return obj


class BaseModelViewSet(LookupIdOrUuidMixin, viewsets.ModelViewSet):
    """Base viewset with common configurations."""

    permission_classes = [AllowAny]  # Default permission, can be overridden in subclasses
    lookup_value_regex = r"(?:\d+|[0-9a-fA-F-]{36})"  # Accept both integer IDs and UUIDs

    # Default filter backends and ordering
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    ordering_fields = "__all__"
    ordering = ["-created_at"]


class BaseSerializer(serializers.ModelSerializer):
    """Base serializer with common configurations."""

    class Meta:
        exclude = ("id", "created_at", "updated_at")
